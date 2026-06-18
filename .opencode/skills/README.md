# OpenCode MLflow Skills

OpenCode skills are stored here. Each skill lives in its own directory with a `SKILL.md` file.

## Local Model Registration Flow

```text
Step 0     model-scenario-orchestrator
Step 1     local-model-intake-flow
Step 2-4   model-project-scan-validation
Step 2-4   mlflow-readiness-validation
Step 5     registration-gap-fill-planning
Step 5     run-model-template-planning
Step 6     prepare-only-validation
Step 7-8   mlflow-registration-execution
Step 1-9   wizard-cli-tui-step-flow
Step 9     registration-result-reporting
```

These skills describe the feature behavior only. They do not create models, implement TUI screens, or run MLflow registration code by themselves.

## Existing MLflow Skill Set

```text
├── agent-evaluation/
├── analyze-mlflow-chat-session/
├── analyze-mlflow-trace/
├── closed-network-validation/
├── error-log-repair/
├── instrumenting-with-mlflow-tracing/
├── job-template-draft/
├── mlflow-ai-gateway/
├── mlflow-experiment-tracking/
├── mlflow-model-registry-deployment/
├── mlflow-onboarding/
├── mlflow-prompt-management/
├── mlflow-prompt-optimization/
├── mlflow-registration-check/
├── querying-mlflow-metrics/
├── retrieving-mlflow-traces/
└── searching-mlflow-docs/
```

The MLflow-specific skills are adapted for this closed-network POC from `mlflow/skills` and `mlflow/mlflow`: tracing, trace analysis, chat session analysis, trace retrieval, agent evaluation, metrics querying, onboarding, documentation search, prompt management, prompt optimization, AI Gateway, experiment tracking, model registry, and deployment.
