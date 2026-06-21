import os

import mlflow


def load_dotenv(path: str = ".env") -> None:
    """python-dotenv 없이 간단한 KEY=VALUE 형식의 .env 파일을 읽는다."""
    if not os.path.exists(path):
        return

    with open(path, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def configure_mlflow() -> None:
    """MLflow 호출이 로컬 3.13 tracking server와 지정 experiment로 향하게 설정한다."""
    load_dotenv()
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5013"))
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "offline-weather-agent-313"))


def qwen_model_name() -> str:
    """provider prefix가 있으면 제거하고 실제 Qwen 모델명만 남긴다."""
    first_openai_model = os.getenv("OPENAI_MODELS", "").split(",", 1)[0].strip()
    model = (
        os.getenv("OPENAI_MODEL")
        or first_openai_model
        or os.getenv("WEATHER_AGENT_MODEL")
        or os.getenv("OPENCODE_MODEL", "qwen2.5-coder:14b")
    )
    if "/" in model:
        return model.rsplit("/", 1)[-1]
    return model


def llm_base_url() -> str:
    """LLM_PROVIDER에 따라 OpenAI 호환 endpoint 주소를 고른다."""
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai":
        return os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    return os.getenv("LOCAL_QWEN_BASE_URL", "http://127.0.0.1:11434/v1").rstrip("/")


def llm_api_key() -> str:
    """OpenAI 방식은 OPENAI_API_KEY, Ollama 방식은 LOCAL_QWEN_API_KEY를 사용한다."""
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai":
        return os.getenv("OPENAI_API_KEY") or os.getenv("LOCAL_QWEN_API_KEY", "ollama")
    return os.getenv("LOCAL_QWEN_API_KEY", "ollama")


def get_genai_module():
    """MLflow 3.13 patch 차이를 고려해 mlflow.genai가 없으면 안전하게 건너뛴다."""
    try:
        import mlflow.genai as genai

        return genai
    except Exception:
        return None
