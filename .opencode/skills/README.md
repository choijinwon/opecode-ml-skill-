# OpenCode MLflow Skills

OpenCode skills are stored here. Each skill lives in its own directory with a `SKILL.md` file.

## Model Test Scenario Flow

```text
Step 0     model-scenario-orchestrator
Step 1     sample-model-matrix-generation
Step 1     model-sample-selection-flow
Step 2-5   model-project-scan-validation
Step 2-5   mlflow-readiness-validation
Step 6     registration-gap-fill-planning
Step 6     run-model-template-planning
Step 7-8   prepare-only-validation
Step 9-10  mlflow-registration-execution
Step 1-10  wizard-cli-tui-step-flow
Step 10    registration-result-reporting
```

These skills describe the feature behavior only. They do not implement sample generation, TUI screens, or MLflow registration code by themselves.

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
