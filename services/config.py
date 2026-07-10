import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    fireworks_api_key: str = os.getenv("FIREWORKS_API_KEY", "")
    fireworks_base_url: str = os.getenv("FIREWORKS_BASE_URL", "https://openrouter.ai/api/v1")
    gemma_model: str = os.getenv("GEMMA_MODEL", "google/gemma-4-26b-a4b-it")

    asr_device: str = os.getenv("ASR_DEVICE", "cpu")
    asr_model_size: str = os.getenv("ASR_MODEL_SIZE", "base")
    asr_compute_type: str = os.getenv("ASR_COMPUTE_TYPE", "int8")
    enable_pitch_analysis: bool = os.getenv("ENABLE_PITCH_ANALYSIS", "true").lower() in ("1", "true", "yes")


settings = Settings()
