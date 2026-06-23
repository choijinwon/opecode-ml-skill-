from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import mlflow
from mlflow.entities import SpanType


SKIP_DIRS = {
    ".git",
    ".next",
    ".nuxt",
    ".svelte-kit",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
}

SOURCE_EXTENSIONS = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".vue",
    ".svelte",
    ".html",
    ".css",
    ".scss",
    ".sass",
    ".less",
}

STYLE_EXTENSIONS = {".css", ".scss", ".sass", ".less"}
COMPONENT_EXTENSIONS = {".jsx", ".tsx", ".vue", ".svelte"}

COLOR_PATTERN = re.compile(
    r"(#[0-9a-fA-F]{3,8}\b|rgba?\([^)]+\)|hsla?\([^)]+\)|\b(?:red|blue|green|black|white|gray|grey|purple|orange|yellow)\b)"
)
CSS_VAR_PATTERN = re.compile(r"--[a-zA-Z0-9-_]+\s*:\s*[^;]+")
FONT_SIZE_PATTERN = re.compile(r"font-size\s*:\s*([^;]+)")
RADIUS_PATTERN = re.compile(r"border-radius\s*:\s*([^;]+)")
SPACING_PATTERN = re.compile(r"(?:margin|padding|gap)\s*:\s*([^;]+)")
CLASS_PATTERN = re.compile(r"className\s*=\s*[\"']([^\"']+)[\"']|class\s*=\s*[\"']([^\"']+)[\"']")


@mlflow.trace(name="analyze_source_project", span_type=SpanType.AGENT)
def analyze_source_project(
    project_path: str,
    user_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, object]:
    """사용자가 지정한 frontend/source 프로젝트를 분석해 디자인 가이드 초안을 만든다."""
    root = Path(project_path).expanduser().resolve()
    trace_user = user_id or "design-source-user"
    trace_session = session_id or "design-source-session"
    mlflow.update_current_trace(
        user=trace_user,
        session_id=trace_session,
        tags={
            "app": "design-agent-ai-studio",
            "domain": "design",
            "mode": "source-analysis",
        },
        metadata={
            "mlflow.trace.user": trace_user,
            "mlflow.trace.session": trace_session,
            "project_path": root.as_posix(),
        },
    )

    files = collect_source_files(root)
    framework = detect_framework(root, files)
    tokens = extract_design_tokens(files)
    catalog = build_component_catalog(root, files)
    guide = write_design_guide(root, framework, files, tokens, catalog)
    return {
        "project_path": root.as_posix(),
        "framework": framework,
        "file_count": len(files),
        "style_file_count": sum(1 for path in files if path.suffix in STYLE_EXTENSIONS),
        "component_count": len(catalog["components"]),
        "tokens": tokens,
        "catalog": catalog,
        "guide_markdown": guide,
    }


@mlflow.trace(name="collect_source_files", span_type=SpanType.TOOL)
def collect_source_files(root: Path) -> list[Path]:
    if not root.exists():
        raise FileNotFoundError(f"프로젝트 경로가 없습니다: {root}")
    if root.is_file():
        return [root] if root.suffix in SOURCE_EXTENSIONS else []

    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and path.suffix in SOURCE_EXTENSIONS:
            files.append(path)
    return sorted(files)


@mlflow.trace(name="detect_frontend_framework", span_type=SpanType.TOOL)
def detect_framework(root: Path, files: list[Path]) -> dict[str, object]:
    package_json = root / "package.json"
    package_text = _read_text(package_json)
    file_names = {path.name for path in files}
    suffixes = Counter(path.suffix for path in files)

    candidates: list[str] = []
    if "next.config.js" in file_names or "next.config.mjs" in file_names or "next" in package_text:
        candidates.append("Next.js")
    if "vite.config.ts" in file_names or "vite.config.js" in file_names or "vite" in package_text:
        candidates.append("Vite")
    if any(path.suffix in {".tsx", ".jsx"} for path in files) or "react" in package_text:
        candidates.append("React")
    if any(path.suffix == ".vue" for path in files) or "vue" in package_text:
        candidates.append("Vue")
    if any(path.suffix == ".svelte" for path in files) or "svelte" in package_text:
        candidates.append("Svelte")
    if "tailwind.config.js" in file_names or "tailwind.config.ts" in file_names or "tailwindcss" in package_text:
        candidates.append("Tailwind CSS")

    return {
        "candidates": sorted(set(candidates)) or ["Unknown"],
        "extension_counts": dict(sorted(suffixes.items())),
    }


@mlflow.trace(name="extract_design_tokens", span_type=SpanType.TOOL)
def extract_design_tokens(files: list[Path]) -> dict[str, object]:
    colors: Counter[str] = Counter()
    css_vars: Counter[str] = Counter()
    font_sizes: Counter[str] = Counter()
    radii: Counter[str] = Counter()
    spacing: Counter[str] = Counter()
    class_names: Counter[str] = Counter()

    for path in files:
        text = _read_text(path)
        if not text:
            continue
        for match in COLOR_PATTERN.findall(text):
            colors[_normalize_space(match)] += 1
        for match in CSS_VAR_PATTERN.findall(text):
            css_vars[_normalize_space(match)] += 1
        for match in FONT_SIZE_PATTERN.findall(text):
            font_sizes[_normalize_space(match)] += 1
        for match in RADIUS_PATTERN.findall(text):
            radii[_normalize_space(match)] += 1
        for match in SPACING_PATTERN.findall(text):
            spacing[_normalize_space(match)] += 1
        for match in CLASS_PATTERN.findall(text):
            value = match[0] or match[1]
            for class_name in value.split():
                class_names[class_name] += 1

    return {
        "colors": _top_items(colors),
        "css_variables": _top_items(css_vars),
        "font_sizes": _top_items(font_sizes),
        "border_radius": _top_items(radii),
        "spacing": _top_items(spacing),
        "class_names": _top_items(class_names, limit=30),
    }


@mlflow.trace(name="build_component_catalog", span_type=SpanType.TOOL)
def build_component_catalog(root: Path, files: list[Path]) -> dict[str, object]:
    component_files = [path for path in files if path.suffix in COMPONENT_EXTENSIONS]
    components = []
    for path in component_files:
        name = path.stem
        text = _read_text(path)
        components.append(
            {
                "name": name,
                "path": path.relative_to(root).as_posix(),
                "uses_button": "<button" in text or "Button" in text,
                "uses_form": "<form" in text or "input" in text or "Input" in text,
                "uses_table": "<table" in text or "Table" in text,
                "uses_modal": "modal" in text.lower() or "dialog" in text.lower(),
                "class_count": len(CLASS_PATTERN.findall(text)),
            }
        )

    directories = Counter(path.parent.relative_to(root).as_posix() for path in component_files)
    return {
        "components": components[:100],
        "component_directories": _top_items(directories, limit=30),
    }


@mlflow.trace(name="write_design_guide", span_type=SpanType.TOOL)
def write_design_guide(
    root: Path,
    framework: dict[str, object],
    files: list[Path],
    tokens: dict[str, object],
    catalog: dict[str, object],
) -> str:
    guide = _render_design_guide(root, framework, files, tokens, catalog)
    return guide


def _render_design_guide(
    root: Path,
    framework: dict[str, object],
    files: list[Path],
    tokens: dict[str, object],
    catalog: dict[str, object],
) -> str:
    components = catalog["components"]
    component_lines = [
        f"- `{item['path']}`: button={item['uses_button']}, form={item['uses_form']}, table={item['uses_table']}, modal={item['uses_modal']}"
        for item in components[:30]
    ]
    if not component_lines:
        component_lines = ["- 컴포넌트 파일을 찾지 못했습니다."]

    return "\n".join(
        [
            "# Design Guide Draft",
            "",
            "## 1. 프로젝트 요약",
            "",
            f"- 분석 경로: `{root.as_posix()}`",
            f"- 추정 framework: {', '.join(framework['candidates'])}",
            f"- 분석 파일 수: {len(files)}",
            f"- 컴포넌트 수: {len(components)}",
            "",
            "## 2. 디자인 토큰 후보",
            "",
            "### 색상",
            _format_token_list(tokens["colors"]),
            "",
            "### CSS 변수",
            _format_token_list(tokens["css_variables"]),
            "",
            "### 글자 크기",
            _format_token_list(tokens["font_sizes"]),
            "",
            "### Radius",
            _format_token_list(tokens["border_radius"]),
            "",
            "### Spacing",
            _format_token_list(tokens["spacing"]),
            "",
            "## 3. 컴포넌트 카탈로그 후보",
            "",
            *component_lines,
            "",
            "## 4. UI 운영 원칙 초안",
            "",
            "- 반복되는 색상과 CSS 변수는 design token으로 승격합니다.",
            "- 버튼, 입력, 카드, 테이블, 모달은 공통 컴포넌트 사용 기준을 문서화합니다.",
            "- 화면별 목적, 주요 행동, 비어있는 상태, 오류 상태, 로딩 상태를 함께 정의합니다.",
            "- 접근성 기준으로 텍스트 대비, 포커스 상태, 키보드 이동, 터치 영역을 점검합니다.",
            "",
            "## 5. 개선 확인 항목",
            "",
            "- 중복 색상/spacing 값을 token으로 통합할 수 있는지 확인합니다.",
            "- 비슷한 역할의 컴포넌트가 여러 경로에 흩어져 있는지 확인합니다.",
            "- 테이블/폼/모달의 상태 표현이 일관적인지 확인합니다.",
            "- 모바일 breakpoint에서 텍스트와 버튼이 겹치지 않는지 확인합니다.",
        ]
    )


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _normalize_space(value: str) -> str:
    return " ".join(value.strip().split())


def _top_items(counter: Counter[str], limit: int = 20) -> list[dict[str, object]]:
    return [{"value": value, "count": count} for value, count in counter.most_common(limit)]


def _format_token_list(items: list[dict[str, object]]) -> str:
    if not items:
        return "- 발견된 값 없음"
    return "\n".join(f"- `{item['value']}` ({item['count']})" for item in items[:20])
