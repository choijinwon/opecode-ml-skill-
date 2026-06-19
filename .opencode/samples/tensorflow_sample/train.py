import json
from pathlib import Path

import numpy as np
import tensorflow as tf


def main():
    root = Path(__file__).resolve().parent
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    artifact_path = root / config["artifact_path"]
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(config["input_size"],)),
            tf.keras.layers.Dense(8, activation="relu"),
            tf.keras.layers.Dense(1, activation="sigmoid"),
        ]
    )
    model.compile(optimizer="adam", loss="binary_crossentropy")

    x = np.array(
        [
            [0.1, 0.2, 0.3, 0.4],
            [0.4, 0.3, 0.2, 0.1],
            [0.9, 0.8, 0.7, 0.6],
            [0.6, 0.7, 0.8, 0.9],
        ],
        dtype=np.float32,
    )
    y = np.array([0, 0, 1, 1], dtype=np.float32)
    model.fit(x, y, epochs=1, verbose=0)
    model.save(artifact_path)
    print(f"saved artifact: {artifact_path}")


if __name__ == "__main__":
    main()
