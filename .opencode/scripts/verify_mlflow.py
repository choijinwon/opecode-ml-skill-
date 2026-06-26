import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class MlflowVerifyReport:
    status: str
    summary: str
    tracking_uri: str | None
    experiment_name: str | None
    experiment_id: str | None
    run_count: int
    latest_run_id: str | None
    artifact_count: int = 0
    model_artifact_found: bool = False
    registry_status: str = "not_requested"
    latest_run_artifacts: list[str] = field(default_factory=list)
    registered_model: str | None = None
    model_versions: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)


def list_artifacts(client, run_id: str, path: str = "") -> list[str]:
    items = []
    for artifact in client.list_artifacts(run_id, path):
        items.append(artifact.path)
        if artifact.is_dir:
            items.extend(list_artifacts(client, run_id, artifact.path))
    return items


def has_model_artifact(artifacts: list[str]) -> bool:
    model_markers = {"MLmodel", "python_model.pkl", "conda.yaml", "requirements.txt"}
    return any(path.rsplit("/", 1)[-1] in model_markers for path in artifacts)


def summarize_report(
    failures: list[str],
    run_count: int,
    artifact_count: int,
    model_artifact_found: bool,
    registry_status: str,
) -> tuple[str, str]:
    if any(item.startswith(("tracking_unreachable", "experiment_missing", "run_missing")) for item in failures):
        return "block", "MLflow 기록 확인이 차단되었습니다. experiment/run 생성 상태를 먼저 확인해야 합니다."
    if failures:
        return "warn", "MLflow run은 확인했지만 artifact/model/registry 항목에 보완이 필요합니다."
    if run_count and artifact_count and (model_artifact_found or registry_status in {"found", "not_requested"}):
        return "pass", "MLflow run, artifact, model 기록 상태가 확인되었습니다."
    return "warn", "MLflow 기본 기록은 일부 확인되었지만 추가 확인이 필요합니다."


def main():
    parser = argparse.ArgumentParser(description="Verify MLflow experiment runs, artifacts, and model registry.")
    parser.add_argument("--tracking-uri", help="MLflow tracking URI")
    parser.add_argument("--experiment-name", help="MLflow experiment name")
    parser.add_argument("--experiment-id", help="MLflow experiment ID")
    parser.add_argument("--registered-model", help="registered model name to inspect")
    parser.add_argument("--max-results", type=int, default=5, help="max runs to inspect")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    failures: list[str] = []
    next_steps: list[str] = []
    try:
        import mlflow
        from mlflow.tracking import MlflowClient
    except Exception as exc:
        raise RuntimeError(f"missing_dependency:mlflow:{exc}") from exc

    if args.tracking_uri:
        mlflow.set_tracking_uri(args.tracking_uri)

    try:
        client = MlflowClient()
        tracking_uri = mlflow.get_tracking_uri()
    except Exception as exc:
        failures.append(f"tracking_unreachable:{exc}")
        next_steps.append("Check the tracking URI, MLflow server status, authentication, or MLflow 3.x backend policy.")
        status, summary = summarize_report(failures, 0, 0, False, "not_requested")
        report = MlflowVerifyReport(
            status=status,
            summary=summary,
            tracking_uri=args.tracking_uri,
            experiment_name=args.experiment_name,
            experiment_id=args.experiment_id,
            run_count=0,
            latest_run_id=None,
            failures=failures,
            next_steps=next_steps,
        )
        if args.json:
            print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
        else:
            print_report(report)
        return

    experiment = None
    try:
        if args.experiment_id:
            experiment = client.get_experiment(args.experiment_id)
        elif args.experiment_name:
            experiment = client.get_experiment_by_name(args.experiment_name)
        else:
            experiment = client.get_experiment_by_name("Default")
    except Exception as exc:
        failures.append(f"tracking_unreachable:{exc}")
        next_steps.append("Check the tracking URI, MLflow server status, authentication, or MLflow 3.x backend policy.")
        status, summary = summarize_report(failures, 0, 0, False, "not_requested")
        report = MlflowVerifyReport(
            status=status,
            summary=summary,
            tracking_uri=tracking_uri,
            experiment_name=args.experiment_name,
            experiment_id=args.experiment_id,
            run_count=0,
            latest_run_id=None,
            failures=failures,
            next_steps=next_steps,
        )
        if args.json:
            print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
        else:
            print_report(report)
        return

    if experiment is None:
        failures.append("experiment_missing")
        next_steps.append("Create or select an MLflow experiment.")
        status, summary = summarize_report(failures, 0, 0, False, "not_requested")
        report = MlflowVerifyReport(
            status,
            summary,
            tracking_uri,
            args.experiment_name,
            args.experiment_id,
            0,
            None,
            failures=failures,
            next_steps=next_steps,
        )
    else:
        runs = client.search_runs([experiment.experiment_id], order_by=["attributes.start_time DESC"], max_results=args.max_results)
        latest_run_id = runs[0].info.run_id if runs else None
        if not runs:
            failures.append("run_missing")
            next_steps.append("Run training or registration code to create an MLflow run.")
        artifacts = list_artifacts(client, latest_run_id) if latest_run_id else []
        if latest_run_id and not artifacts:
            failures.append("artifact_missing")
            next_steps.append("Log model artifacts or outputs inside the MLflow run.")
        model_artifact_found = has_model_artifact(artifacts)
        if artifacts and not model_artifact_found:
            failures.append("model_artifact_missing")
            next_steps.append("Confirm mlflow.pyfunc.log_model or equivalent model logging.")

        versions: list[str] = []
        registry_status = "not_requested"
        if args.registered_model:
            try:
                found = client.search_model_versions(f"name = '{args.registered_model}'")
                versions = [str(version.version) for version in found]
                if not versions:
                    registry_status = "missing"
                    failures.append("registry_missing")
                    next_steps.append("Register the logged model or verify the registered model name.")
                else:
                    registry_status = "found"
            except Exception as exc:
                registry_status = "error"
                failures.append(f"registry_missing:{exc}")

        status, summary = summarize_report(failures, len(runs), len(artifacts), model_artifact_found, registry_status)
        report = MlflowVerifyReport(
            status=status,
            summary=summary,
            tracking_uri=tracking_uri,
            experiment_name=experiment.name,
            experiment_id=experiment.experiment_id,
            run_count=len(runs),
            latest_run_id=latest_run_id,
            artifact_count=len(artifacts),
            model_artifact_found=model_artifact_found,
            registry_status=registry_status,
            latest_run_artifacts=artifacts,
            registered_model=args.registered_model,
            model_versions=versions,
            failures=failures,
            next_steps=next_steps,
        )

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print_report(report)


def print_report(report: MlflowVerifyReport):
    print("MLflow Analysis Report")
    print(f"Status: {report.status}")
    print(f"Summary: {report.summary}")
    print()
    print(f"Tracking URI: {report.tracking_uri}")
    print(f"Experiment: {report.experiment_name or 'missing'} ({report.experiment_id or 'missing'})")
    print(f"Run count: {report.run_count}")
    print(f"Latest run: {report.latest_run_id or 'missing'}")
    print(f"Artifact count: {report.artifact_count}")
    print(f"Model artifact found: {report.model_artifact_found}")
    print("Artifacts:")
    for artifact in report.latest_run_artifacts:
        print(f"- {artifact}")
    if report.registered_model:
        print(f"Registered model: {report.registered_model}")
        print(f"Registry status: {report.registry_status}")
        print(f"Versions: {', '.join(report.model_versions) if report.model_versions else 'missing'}")
    if report.failures:
        print("Failures:")
        for failure in report.failures:
            print(f"- {failure}")
    if report.next_steps:
        print("Next steps:")
        for step in report.next_steps:
            print(f"- {step}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)
