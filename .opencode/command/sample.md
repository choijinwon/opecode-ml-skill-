---
description: Copy one bundled model sample folder into the current workspace.
agent: launch
---

Copy the selected model sample folder into the current workspace.

Accepted sample names:

```text
sklearn
pytorch
tensorflow
```

Rules:

- If the user did not provide a sample name, ask them to choose `sklearn`, `pytorch`, or `tensorflow`.
- If the user provided `sklearn`, run:

```text
python .opencode/scripts/bootstrap_sample_project.py --project . --sample sklearn --execute
```

- If the user provided `pytorch`, run:

```text
python .opencode/scripts/bootstrap_sample_project.py --project . --sample pytorch --execute
```

- If the user provided `tensorflow`, run:

```text
python .opencode/scripts/bootstrap_sample_project.py --project . --sample tensorflow --execute
```

- The script must create `<workspace>/<sample>_sample/`.
- Do not copy sample contents directly into the workspace root.
- After execution, report the `target_project_path`.
- If the target sample folder already exists, stop and explain that `--force` is required to overwrite it.
