# Pocket Interview Coach — lablab.ai Submission Kit

Everything you need to fill in the AMD Developer Hackathon Act II (Unicorn Track) submission form,
plus the slide outline, the video script, and the "challenges I faced" narrative.

Copy each field straight into the lablab.ai form.

---

## 📋 BASIC INFORMATION

### Project Title
```
Pocket Interview Coach
```
(Optional tagline for the subtitle field: *"Your AI interview coach that scores what you say and how you say it."*)

### Short Description (one line)
```
An AI mock-interview coach that scores both your content and your delivery (pace, tone, filler words) — Gemma 4 coaches you, and an independent Fireworks model on AMD GPUs acts as the hiring manager who makes the call.
```

### Long Description
```
THE PROBLEM
Most people fail interviews not because they lack the skills, but because they can't perform under pressure — they ramble, fill silences with "um", speak in a monotone, or forget to give concrete results. Human mock interviews are expensive and hard to schedule, and text-based AI prep tools completely ignore HOW you speak, which is half of what an interviewer actually judges.

THE SOLUTION
Pocket Interview Coach is a voice-first mock-interview simulator. You pick a role (and optionally a company, job description, resume, persona, and difficulty), and it runs a realistic spoken interview. For every answer you record out loud, it analyzes BOTH dimensions of a real interview:

• CONTENT — structure (STAR method), specificity, and whether you actually answered the question.
• DELIVERY — words-per-minute pace, vocal tone/expressiveness, filler-word count, pauses, and volume steadiness, extracted directly from your voice signal.

It then coaches you in plain English ("you sped up to 180 wpm in the second half — that read as nervous"), scores each answer 0–100 on content and delivery, asks devil's-advocate follow-up questions when an answer leaves something unexplored, and ends with a full readiness report, a personalized cheat sheet, and downloadable PDF/JSON/transcript exports.

THE TWIST: TWO AIs, TWO ROLES
The app runs two different models for two different jobs, which mirrors a real hiring loop:
• Gemma 4 is your COACH — it generates the questions, scores content and delivery, asks follow-ups, and writes your cheat sheet.
• A Fireworks-hosted model running on AMD Instinct GPUs is the HIRING MANAGER — it independently reviews the whole interview and commits to a real Strong-Hire → No-Hire verdict, with a confidence score, the single strongest reason to hire you, your biggest red flag, and your standout moment. The same Fireworks model also powers "Level up this answer," rewriting your own answer into a stronger version grounded in what you actually said.

Using two independent providers/models is the point: the final verdict is a genuine second opinion, not the same model grading its own coaching.

USE OF AMD
The independent hiring-manager model is served by Fireworks AI, which runs on AMD Instinct GPUs — so the "hire or not" decision, the highest-stakes call in the product, is computed on AMD hardware. The local voice-analysis pipeline (speech-to-text + prosody) is CPU today with a documented one-env-var switch to ROCm/AMD-GPU acceleration.

WHY IT MATTERS (product/market)
Interview prep is a large, evergreen market (new grads, career switchers, laid-off workers, sales/PM/consulting candidates who live and die by verbal performance). Existing tools grade text; almost none grade voice and delivery. Pocket Interview Coach is the practice partner you can use at 2am, as many times as you want, that tells you not just what to say but how you're coming across — and then tells you whether you'd get the job.

TECH
Streamlit single-process app (fully containerized with Docker), Gemma 4 via an OpenAI-compatible API, a Fireworks-hosted model (gpt-oss-120b) on AMD, faster-whisper for speech-to-text, librosa for prosody/delivery metrics, Plotly for the gauges/radars/trend charts, and fpdf2 for report export. Deployed publicly on Streamlit Community Cloud.
```

### Technology and Category Tags
```
Gemma, Gemma 4, Fireworks AI, AMD, AMD Instinct, Streamlit, Python, Speech Recognition,
Whisper, faster-whisper, librosa, NLP, LLM, Voice AI, Prosody Analysis, Plotly,
EdTech, Career Tech, Interview Preparation, Productivity, Docker
```
Primary category: **Productivity / EdTech / Career**

---

## 📸 COVER IMAGE AND PRESENTATION

### Cover Image (what to make — 1200×630 or 1280×720)
Dark background (#0b0b12) matching the app. Layout:
- **Left:** the product name "Pocket Interview Coach" in a cyan→purple gradient (colors `#2dd4ee` → `#9b6bff`), with the tagline "Scores what you say AND how you say it" underneath.
- **Right:** a clean screenshot of the report screen showing the two score gauges (Content / Delivery) and the 🔥 hiring-verdict badge.
- **Bottom strip / badges:** three small pills — "🧠 Gemma 4 coach", "🔥 Fireworks on AMD", "🎙️ Voice-first".
Fastest way to make it: take a real screenshot of your report page, paste it on the right half of a dark Canva/Figma frame, add the title text on the left. (Ask me and I can generate a ready-to-export SVG cover.)

### Video Presentation
2–3 minute screen recording. Full script and shot list in the **VIDEO SCRIPT** section below.
Upload to YouTube (unlisted is fine) and paste the link.

### Slide Presentation
10-slide deck. Full content in the **SLIDE DECK** section below.
Build in Google Slides / Canva / Gamma, export to PDF or share the link.

---

## 💻 APP HOSTING AND CODE REPOSITORY

### Public GitHub Repository
```
https://github.com/sanjai-b-2006/pocket_intervie_streamlit
```

### Demo Application Platform
```
Streamlit Community Cloud
```

### Application URL
```
https://pocket-interview.streamlit.app
```
(Confirm this is the exact URL shown in your Streamlit Cloud dashboard before submitting.)

### Containerization note (a hackathon requirement — mention it in the README/submission)
The repo includes a `Dockerfile`; the app runs with:
```
docker build -t pocket-interview-streamlit .
docker run -p 8501:8501 --env-file .env pocket-interview-streamlit
```
Streamlit Cloud itself builds from `requirements.txt` + `packages.txt`, but the container satisfies the "all submissions must be containerized" rule and lets judges self-host.

---

## 🎬 VIDEO SCRIPT (2–3 minutes)

Record your screen (OBS / Loom / built-in screen recorder) with mic audio. Keep it tight and energetic.
Format: **[SHOT] what's on screen — "what you say"**

**[0:00–0:15] HOOK — your face or the landing page**
> "Most people don't fail interviews because they're unqualified. They fail because they ramble, they say 'um' twenty times, and they freeze up. I built Pocket Interview Coach to fix exactly that — it grades not just WHAT you say, but HOW you say it."

**[0:15–0:35] SETUP — show the setup screen, fill it in live**
> "I pick a role — let's say UX Designer at Figma. I can add a job description, upload my resume, choose an interviewer persona, pick a difficulty, even turn on a pressure timer."
Click **Start Mock Interview**.

**[0:35–1:05] THE INTERVIEW — record a real spoken answer**
> "It generates a tailored interview with Gemma 4. Here's the first question — I'll answer it out loud, exactly like the real thing."
Hit **Record answer**, give a short answer (deliberately include an "um" and speak a bit fast), hit **Stop & analyze**.
> "It's transcribing my voice and pulling out my pace, my tone, my filler words — all from the audio."

**[1:05–1:40] THE FEEDBACK — this is the money shot**
> "And here's what makes it different. Two scores: content AND delivery. It caught that I spoke at 175 words a minute and used two filler words. It gives me plain-English coaching on both. There's a STAR-method checklist, a radar breakdown, and I can even play back my own answer."
Point at the follow-up toast: > "It even threw a devil's-advocate follow-up question at me, just like a real interviewer."
Click **⚡ Level up this answer**: > "And this rewrites MY answer into a stronger version — running on a Fireworks model on AMD GPUs."

**[1:40–2:15] THE REPORT + THE VERDICT — the wow ending**
> "At the end, I get a full readiness report — an overall grade, score trends, a personalized cheat sheet, and exports."
Scroll to the 🔥 verdict card: > "And here's the twist. Gemma 4 was my coach — but an INDEPENDENT model on AMD hardware plays the hiring manager and makes the actual call: hire, or no-hire, with the reasons for and against. Two AIs, two roles, just like a real hiring loop."

**[2:15–2:35] CLOSE**
> "Pocket Interview Coach — practice out loud, get coached on your content and your delivery, and find out if you'd actually get the job. It's live, it's open source, and it's built on Gemma 4 and Fireworks on AMD. Thanks for watching."

### Recording tips
- Do ONE practice run first so the app's models are "warm" (first call after idle is slower).
- Pre-fill the setup so you're not typing on camera for 30 seconds — or speed that part up in editing.
- Make sure `JUDGE_API_KEY` is set in Streamlit secrets **before** recording so the 🔥 verdict actually appears.
- Have the verdict already generated once (it caches) so it pops instantly on camera.
- Keep answers SHORT (10–15 seconds) so the analysis returns fast on video.
- Record at 1080p, hide bookmarks/personal tabs, use a clean browser window.

---

## 🖥️ SLIDE DECK (10 slides)

**Slide 1 — Title**
Pocket Interview Coach
"Scores what you say AND how you say it."
Your name · AMD Developer Hackathon Act II · Unicorn Track
Logos: Gemma · Fireworks AI · AMD · Streamlit

**Slide 2 — The Problem**
- People fail interviews on *delivery*, not just knowledge: rambling, filler words, monotone, no concrete results.
- Human mock interviews are expensive and hard to schedule.
- Text-based AI prep ignores HOW you sound — half of what interviewers judge.

**Slide 3 — The Solution**
A voice-first mock-interview simulator that coaches you on BOTH:
- Content (structure, STAR, specificity)
- Delivery (pace, tone, fillers, pauses) — extracted from your actual voice.
Practice out loud, unlimited, any time.

**Slide 4 — How It Works (pipeline diagram)**
Your voice → faster-whisper (speech-to-text) + librosa (prosody metrics) → Gemma 4 (content + delivery coaching, scores, follow-ups) → Report + Fireworks hiring verdict.
Callout: local voice analysis + cloud reasoning.

**Slide 5 — The Twist: Two AIs, Two Roles**
- 🧠 Gemma 4 = the COACH (questions, scoring, follow-ups, cheat sheet).
- 🔥 Fireworks model on AMD = the HIRING MANAGER (independent hire/no-hire verdict + answer rewrite).
- Two independent models = a real second opinion, not self-grading.

**Slide 6 — Use of AMD**
- The highest-stakes decision (hire or not) runs on a Fireworks model served by AMD Instinct GPUs.
- Local ASR/prosody is CPU today with a one-env-var switch to ROCm/AMD-GPU acceleration (documented).

**Slide 7 — Feature Highlights (screenshot grid)**
Personas & panel mode · resume-aware questions · devil's-advocate follow-ups · STAR checklist · performance radar · delivery timeline · readiness grade · cheat sheet · JD keyword coverage · PDF/JSON export · re-record · TTS question playback.

**Slide 8 — Product & Market**
- Huge evergreen market: new grads, career switchers, laid-off workers, sales/PM/consulting candidates.
- Existing tools grade text; almost none grade voice + delivery.
- The 2am practice partner that tells you if you'd get the job.

**Slide 9 — Engineering Journey (challenges)**
Gemma not yet on Fireworks → dual-provider design. Hosting friction (HF quota, Render OOM/CORS) → pivot to Streamlit. Python 3.14 wheel failures, mic format bug, PDF cursor bug, reasoning-model token truncation → all diagnosed and fixed. (Full log in changes.md.)

**Slide 10 — Live + Links**
"It's live and open source."
App: pocket-interview.streamlit.app
Repo: github.com/sanjai-b-2006/pocket_intervie_streamlit
Built on Gemma 4 · Fireworks AI · AMD · Streamlit
Thank you / QR code to the app.

---

## 🧗 CHALLENGES I FACED (narrative — for the deck, the writeup, or to talk over)

This is the honest engineering story. It shows resilience and real debugging, which judges reward.

1. **Gemma 4 wasn't deployed on the Fireworks account.** The plan was to run Gemma 4 on Fireworks (the hackathon's AMD-hosted provider), but every Gemma slug returned "not deployed," and `/v1/models` confirmed no Gemma on the key. Rather than block, I used OpenRouter for Gemma 4 AND turned the constraint into a feature: the Fireworks key now powers an *independent* hiring-manager model — a genuinely better design than one model doing everything.

2. **Hosting was a gauntlet.** Hugging Face Spaces hit a CPU quota wall before building. Render (free tier) worked but threw three separate issues — a CORS rejection, a silently-empty API-key field (401s), and out-of-memory crashes from the whisper+librosa+numba stack blowing past the 512MB cap mid-request (which looked like an infinite "Analyzing…" hang). I diagnosed and fixed each, then made the call to rebuild on Streamlit Community Cloud for a far simpler, more reliable free-hosting story.

3. **Streamlit Cloud provisioned Python 3.14**, for which `av`/`numpy`/`pandas` had no prebuilt wheels, so pip tried to compile everything from source and appeared to hang. Fixed by pinning Python 3.11 (via the app's Settings, since `runtime.txt` only applies at first creation) and adding the FFmpeg dev headers to `packages.txt`.

4. **Real bugs caught by testing, not assuming:** the mic recorder defaulted to webm while the code saved .wav (caught by reading the library's actual source); the PDF exporter crashed on cursor drift (caught by unit-testing the export path directly); and the Fireworks reasoning model returned empty content because hidden reasoning ate the entire token budget (caught by running it against the live API). Each was root-caused and fixed, not worked around.

5. **The lesson:** almost every wall became a better product — the Fireworks constraint produced the dual-AI design, and the hosting pain produced a clean, containerized, one-command app anyone can run.

---

## ✅ PRE-SUBMISSION CHECKLIST
- [ ] `JUDGE_API_KEY` (+ `JUDGE_BASE_URL`, `JUDGE_MODEL`) set in Streamlit Cloud **Secrets** so the 🔥 verdict works.
- [ ] `FIREWORKS_API_KEY` / `FIREWORKS_BASE_URL` / `GEMMA_MODEL` set for the Gemma coach.
- [ ] App loads at the public URL and a full session runs end-to-end.
- [ ] Repo is **public** and README has setup + usage (it does).
- [ ] Dockerfile present (containerization requirement) ✅.
- [ ] Cover image made and uploaded.
- [ ] 2–3 min video recorded and uploaded (link ready).
- [ ] Slides exported to PDF / link ready.
- [ ] Every form field above pasted in.
- [ ] Submitted on lablab.ai **before the deadline**.
```
