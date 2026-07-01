from __future__ import annotations

import json
from pathlib import Path


LOCAL_SERVING_DIR = Path(__file__).resolve().parent
AI_STUDIO_DIR = LOCAL_SERVING_DIR.parent
PROJECT_DIR = AI_STUDIO_DIR.parent

# AIU Studio template: prepare_selected_model.py rewrites these values for the selected model.
SOURCE_MODEL_PATH = PROJECT_DIR / "data" / "model.joblib"
DATA_MODEL_PATH = SOURCE_MODEL_PATH
MODEL_PATH = SOURCE_MODEL_PATH
MODEL_KIND = "unknown"


def load_selected_model():
    raise ValueError(f"unsupported MODEL_KIND: {MODEL_KIND}")


def load_input_example():
    input_path = AI_STUDIO_DIR / "input_example.json"
    if input_path.is_file():
        return json.loads(input_path.read_text(encoding="utf-8"))
    return {}


def main():
    model = load_selected_model()
    print(
        json.dumps(
            {
                "status": "loaded",
                "model_kind": MODEL_KIND,
                "model_path": str(MODEL_PATH),
                "model_type": type(model).__name__,
                "input_example": load_input_example(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
