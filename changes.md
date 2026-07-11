# Changes & Problem Log

A running record of what broke, why, and how it got fixed while building Pocket Interview Coach for
the AMD Developer Hackathon Act II (Unicorn Track). Kept here so the reasoning behind each decision
survives past any one conversation.

## 1. Original build: FastAPI + Next.js

The first version was a two-service app: FastAPI backend (question generation via Gemma 4, speech-to-
text via `faster-whisper`, delivery-metric analysis via `librosa`, SQLite storage) + a Next.js
frontend (setup screen, live recording session, report dashboard), containerized with
`docker-compose`. This is still the more feature-complete version (live in-recording coaching, TTS,
animations, PWA install support, localStorage-based history/gamification) — see
`pocket-interview-coach/README.md` in the sibling project.

Features layered on over time: company field + guaranteed basic warm-up question, resume upload,
experience-level calibration, easy→hard question ordering, BYOK settings page, interviewer personas,
panel mode, adjacent practice tracks (salary negotiation, performance review, difficult feedback),
weakness-drill mode, AI-generated devil's-advocate follow-up questions, per-answer delivery
timelines, and personalized cheat sheets.

## 2. Gemma 4 wasn't available on Fireworks yet

Plan: use Fireworks AI (the hackathon's designated AMD-hardware-hosted provider) for Gemma 4. In
practice, every Gemma model slug tried (`gemma-4-26b-a4b-it`, `gemma-4-31b-it`, `gemma-3-27b-it`,
etc.) returned `"Model not found, inaccessible, and/or not deployed"` on the account's Fireworks key
— confirmed by checking `/v1/models`, which listed only 7 unrelated models, no Gemma at all. This
looked like an account-provisioning issue on Fireworks' side (likely something the hackathon
organizers still needed to enable), not a bug in our code.

**Fix (temporary):** switched to **OpenRouter**, which does host `google/gemma-4-26b-a4b-it` and
responded correctly immediately. `FIREWORKS_BASE_URL`/`FIREWORKS_API_KEY`/`GEMMA_MODEL` were kept as
generic env var names so swapping back to real Fireworks access (once granted) is a one-line change,
no code changes needed.

## 3. Hosting attempts and why each one hit a wall

The app needed a public URL for the hackathon submission (`docker-compose` on a personal machine
isn't a valid "Application URL"). Several free options were tried:

- **Hugging Face Spaces** — hit `"You've reached your cpu-basic quota limit"` before the app even
  built. HF's free tier caps concurrently-running Spaces per account; with nothing else running,
  this was most likely tied to account verification status, not anything we could fix in code.
- **AMD Developer Cloud GPU pod** (`notebooks.amd.com/hackathon`) — this turned out to be a
  Jupyter-notebook compute environment for running/benchmarking models on real AMD GPUs, not a
  public web host. Confirmed the GPU (`rocm-smi` showed a real AMD Instinct-class device) but no
  PyTorch/ML stack was pre-installed, and `faster-whisper`'s backend (`ctranslate2`) doesn't have a
  ROCm build anyway — only CPU/NVIDIA-CUDA. Real GPU acceleration here would need swapping the ASR
  library to a `transformers`-based Whisper pipeline running on ROCm-enabled PyTorch — noted as a
  possible future improvement, not done.
- **Render (free tier)** — this is where the app actually got hosted. Backend on Render, frontend on
  Vercel. Hit three separate issues here, each diagnosed and fixed in turn:

  1. **CORS rejection.** `CORS_ORIGINS` on Render was still the default (`http://localhost:3000`)
     after the Vercel frontend was deployed, so every request from the real Vercel URL was rejected
     with `"Disallowed CORS origin"`. Fixed by updating the env var to the actual Vercel domain.
  2. **Missing API key.** After CORS was fixed, requests failed with `401 Missing Authentication
     header` — the `FIREWORKS_API_KEY` env var on Render had never actually been filled in (empty
     field). Fixed by pasting in the real OpenRouter key.
  3. **Out-of-memory crashes.** Render's free tier caps instances at **512MB RAM**. The ASR/prosody
     pipeline (`faster-whisper`/`ctranslate2` + `librosa` + `numba` JIT-compiling the pitch-tracking
     function at first call + numpy/scipy) is memory-hungry enough to exceed that during a request,
     triggering Render's automatic OOM restart — which is exactly why answer submissions would hang
     on "Analyzing..." forever (the instance restarted mid-request, silently dropping the
     connection). Partially mitigated by adding an `ENABLE_PITCH_ANALYSIS` env var (skip the
     numba-JIT pass entirely on constrained hosts) and letting `ASR_MODEL_SIZE` drop to `tiny`, plus
     right-sizing every LLM call's `max_tokens` (was a flat 1200 for every call regardless of need)
     to cut both latency and truncation risk.

  Even after these fixes, Render's free tier remained fundamentally tight for this workload — cold
  starts add 50+ seconds on top of genuine multi-second ASR+LLM processing time, and the memory
  ceiling stays a risk under any real load.

## 4. Why we moved to Streamlit

Given repeated friction with general-purpose Python hosting platforms, the call was made to rebuild
the app in **Streamlit** and deploy to **Streamlit Community Cloud**, which is free, Python-native,
and purpose-built for exactly this kind of app rather than a generic Docker host. This was a
deliberate trade-off, not a strict upgrade:

**What Streamlit gains:** a much simpler, more reliable free-hosting story — no separate
frontend/backend deploy, no CORS configuration, no Docker Compose orchestration to get wrong.

**What Streamlit loses** (Streamlit's rerun-based execution model doesn't support these without
heavy custom-component work): live in-recording pace/filler coaching, the animated waveform
visualizer and page-transition animations, and PWA install support. Cross-session history/
gamification was also dropped, since Streamlit sessions don't carry a per-browser identity the way
`localStorage` did in the React app.

**What ported over unchanged:** the entire AI pipeline — question generation with personas/session
types/drill mode, ASR, prosody/delivery-metric extraction, scoring, devil's-advocate follow-ups,
delivery timelines, and cheat sheet generation are the *same tested Python code*, just re-imported
under `services/` with no HTTP layer in between (Streamlit calls the service functions directly, no
FastAPI needed).

## 5. Bug caught during the Streamlit rebuild

`streamlit-mic-recorder`'s `mic_recorder()` defaults to `format="webm"`, but the initial code saved
the returned bytes to a file with a `.wav` extension — a real format/extension mismatch that would
have broken transcription. Caught by reading the library's actual installed source
(`streamlit_mic_recorder/__init__.py`) rather than assuming its API, which also revealed that
`format="wav"` is an explicitly supported option (used internally by the library's own
`speech_to_text` helper). Fixed by passing `format="wav"` explicitly.

## 6. Verification approach

Browser automation tools weren't available in-session to click through the rendered UI directly, so
verification leaned on a headless integration test that imports `services/interview.py` directly and
exercises `create_session` → `process_answer` → `build_report` → `build_cheat_sheet` against the real
Gemma 4 API, using a synthetic WAV file (pure Python `wave` module, no `ffmpeg` needed on the host).
This confirmed panel-mode persona rotation, scoring, delivery timelines, and — notably — the
devil's-advocate follow-up question actually firing when the (deliberately garbled) test transcript
was unclear, proving that code path end-to-end rather than just by inspection.

## 7. Extra features added after the initial Streamlit port

Once the base rebuild was verified, a second pass added features specifically chosen to fit
Streamlit's execution model well (as opposed to the ones explicitly dropped in section 4):

- **STAR-method breakdown** — `generate_answer_feedback`'s prompt now also returns a
  `star_components` object (situation/task/action/result booleans), rendered as a checklist so the
  candidate can see exactly which part of the STAR structure their answer was missing.
- **Multi-axis performance radar chart** (Plotly `Scatterpolar`) — content, delivery, pace-vs-ideal,
  tone expressiveness, and low-filler-usage on one glanceable chart, both per-answer and averaged
  across the whole session on the report page.
- **Own-answer playback** — the raw recorded audio bytes are now kept on the `Answer` object so
  `st.audio()` can play back exactly what you said, right next to the feedback.
- **Interview readiness score + letter grade** (60/40 weighted blend of content/delivery scores),
  with `st.balloons()` firing once per session on a strong (A/B) result.
- **Exports**: PDF (via `fpdf2`), plain-text transcript, and JSON, all as one-click download buttons
  on the report page.
- **"Surprise me" role randomizer** and an optional **visual countdown timer** during recording
  (implemented as a display-only embedded JS clock via `st.components.v1.html`, since the
  `streamlit-mic-recorder` component doesn't expose a JS hook we can call into to auto-stop
  recording — it's a pressure cue, not an enforced cutoff).

### Bug caught while adding these: `fpdf2` "Not enough horizontal space"

The first PDF-export implementation mixed `cell(0, h, text, ln=True)` (legacy line-break API) with
`multi_cell(0, h, text)` calls, and crashed with `FPDFException: Not enough horizontal space to
render a single character` on the second question's transcript line — the cell/multi_cell cursor
tracking drifted enough that the reported available width hit zero. Root-caused by testing the
export functions directly against a small synthetic session (no LLM call needed to test this path)
rather than assuming the first draft worked. Fixed by dropping `cell(..., ln=True)` entirely,
routing every text block through `multi_cell` with an explicit `pdf.set_x(pdf.l_margin)` reset
beforehand, which eliminates the ambiguity instead of just working around one instance of it.

## 8. Streamlit Community Cloud build failure: wrong Python version

First deploy attempt failed during dependency install: `av==12.3.0` (a `faster-whisper` dependency)
tried to build from source and failed with `pkg-config is required for building PyAV`, and the
fallback pip install path then got stuck compiling `numpy`/`pandas` from source too (extremely slow,
looked "stuck" but was really just a multi-minute C/Cython build). Root cause: Streamlit Cloud had
provisioned a **Python 3.14** environment for the app, and none of `av`, `numpy==1.26.4`, or
`pandas==2.2.3`'s pinned versions publish prebuilt wheels for that (very new) Python version yet, so
pip had to compile everything from source instead of just downloading a wheel.

**Fix:** added `runtime.txt` (`python-3.11`) to pin Streamlit Cloud to a Python version every pinned
package has prebuilt wheels for, avoiding source builds entirely. Also expanded `packages.txt` beyond
just `ffmpeg` to include `pkg-config` and the FFmpeg development headers (`libavformat-dev`,
`libavcodec-dev`, etc.) as a safety net, since `av`'s source build needs those specifically (the
`ffmpeg` binary alone isn't enough to build `PyAV` from source, only to run it at runtime).

**Follow-up:** `runtime.txt` turned out to only take effect at *initial app creation* — an already-
provisioned app kept its Python 3.14 environment on redeploy. The reliable fix is to set the Python
version explicitly in the app's **Settings → General → Python version** on share.streamlit.io (or
delete and recreate the app), which forces a fresh 3.11 environment with prebuilt wheels.

## 9. Actually using the Fireworks API (dual-AI design)

The whole premise of the hackathon is Fireworks AI credits on AMD hardware, but Gemma 4 still isn't
deployed on the Fireworks account (re-checked with the fresh key: `/v1/models` returns
`gpt-oss-120b`, `deepseek-v4-pro`, `glm-5p2`, `kimi-k2p5/p6`, `flux-1-schnell` — strong models, just
no Gemma). Rather than leave the Fireworks key unused, the app now runs **two different models for
two different jobs**:

- **Gemma 4 (via OpenRouter) = the coach** — generates questions, scores each answer's content and
  delivery, asks devil's-advocate follow-ups, writes the cheat sheet.
- **A Fireworks-hosted model on AMD Instinct GPUs = the hiring manager** (`services/fireworks.py`) —
  independently reviews the whole interview and commits to a real **Strong Hire → No-Hire verdict**
  with confidence, rationale, case-for/case-against, and a standout moment. It also powers
  **"⚡ Level up this answer"**, rewriting the candidate's *own* answer into a stronger version
  (grounded in what they actually said — the prompt explicitly forbids inventing achievements).

Using two independent providers/models is the point: the verdict is a genuine second opinion, not
the same model grading its own coaching. It's wired through separate env vars (`JUDGE_API_KEY` /
`JUDGE_BASE_URL` / `JUDGE_MODEL`) so it stays cleanly decoupled from the Gemma path, and the feature
degrades gracefully (hidden with a hint) if no Fireworks key is set.

**Bug caught while building it — reasoning models eat the token budget.** `gpt-oss-120b` is a
reasoning model: it spends completion tokens on hidden reasoning *before* emitting the visible
`content`. With `max_tokens=400` on the answer-rewrite call, reasoning consumed the entire budget and
the API returned an empty `content` field, which blew up as `KeyError: 'content'`. Caught by running
the verdict + rewrite against the real Fireworks API with a synthetic session (no browser needed).
Fixed by (a) raising the token budgets to ~1400 so there's room for real output after reasoning, and
(b) handling an empty `content` explicitly with a clear "likely truncated, try again" error instead
of a downstream crash. Also normalized Unicode dashes (the model sometimes writes "No‑Hire" with a
non-breaking hyphen) before matching the decision against the known set, so the verdict badge/color
lookup doesn't silently fall through.

**Also added** (no API needed): a **job-description keyword-coverage meter** — extracts the
meaningful keywords from the pasted JD and shows which ones the candidate actually said out loud
across their answers vs. which they missed — plus a "how it works" strip on the landing page and a
"Coach: Gemma 4 / Hiring manager: Fireworks on AMD" credit in the sidebar.

**Note on the local test discrepancy:** the dev machine has legacy `PyFPDF 1.7.2` installed, whose
`output()` prints to a cp1252 console and crashes on non-latin characters. The app pins **`fpdf2`**
in `requirements.txt` (a different, incompatible library despite the similar name), which is what
runs on Streamlit Cloud and handles the export correctly — so a local PDF-export crash here is an
environment artifact, not an app bug.
