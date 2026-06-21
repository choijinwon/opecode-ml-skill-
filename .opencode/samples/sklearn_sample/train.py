import json
from pathlib import Path

import joblib
import mlflow
import numpy as np
from sklearn.linear_model import LogisticRegression


def main():
    mlflow.set_tracking_uri("http://127.0.0.1:5001")
    mlflow.set_experiment("sklearn-tracing-test")
    mlflow.sklearn.autolog()
    root = Path(__file__).resolve().parent
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    artifact_path = root / config["artifact_path"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    x = np.array(
        [
            [5.1, 3.5, 1.4, 0.2],
            [4.9, 3.0, 1.4, 0.2],
            [6.2, 3.4, 5.4, 2.3],
            [5.9, 3.0, 5.1, 1.8],
        ]
    )
    y = np.array([0, 0, 1, 1])
    model = LogisticRegression(random_state=42)
    model.fit(x, y)
    joblib.dump(model, artifact_path)
    print(f"saved artifact: {artifact_path}")


if __name__ == "__main__":
    main()
