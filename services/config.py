import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Primary reasoning engine (Gemma 4). Runs through OpenRouter today because Gemma 4
    # isn't deployed on the hackathon Fireworks account yet; swap the three vars below back
    # to Fireworks once it is, no code change needed.
    fireworks_api_key: str = os.getenv("FIREWORKS_API_KEY", "")
    fireworks_base_url: str = os.getenv("FIREWORKS_BASE_URL", "https://openrouter.ai/api/v1")
    gemma_model: str = os.getenv("GEMMA_MODEL", "google/gemma-4-26b-a4b-it")

    # Independent "hiring manager" model, served by Fireworks AI on AMD Instinct GPUs.
    # A genuinely different provider/model from the coach above, so the verdict is a true
    # second opinion rather than the same model grading itself.
    judge_api_key: str = os.getenv("JUDGE_API_KEY", "")
    judge_base_url: str = os.getenv("JUDGE_BASE_URL", "https://api.fireworks.ai/inference/v1")
    judge_model: str = os.getenv("JUDGE_MODEL", "accounts/fireworks/models/gpt-oss-120b")

    asr_device: str = os.getenv("ASR_DEVICE", "cpu")
    asr_model_size: str = os.getenv("ASR_MODEL_SIZE", "base")
    asr_compute_type: str = os.getenv("ASR_COMPUTE_TYPE", "int8")
    enable_pitch_analysis: bool = os.getenv("ENABLE_PITCH_ANALYSIS", "true").lower() in ("1", "true", "yes")


settings = Settings()
