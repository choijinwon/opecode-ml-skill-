"""폐쇄망 RAG 검색에 사용할 작은 로컬 지식 문서 모음."""

LOCAL_DOCUMENTS = [
    {
        "id": "weather_scope",
        "title": "날씨 에이전트 범위",
        "text": (
            "이 에이전트는 서울, 부산, 제주, 대구, 인천의 샘플 날씨 데이터를 제공한다. "
            "외부 인터넷 날씨 API는 호출하지 않고 로컬에 포함된 데이터만 사용한다."
        ),
    },
    {
        "id": "closed_network",
        "title": "폐쇄망 운영",
        "text": (
            "폐쇄망에서는 Ollama OpenAI-compatible endpoint와 로컬 MLflow Tracking 서버를 사용한다. "
            "Python 패키지는 사내 PyPI 또는 wheelhouse로 반입해야 한다."
        ),
    },
    {
        "id": "mlflow_sessions",
        "title": "MLflow Chat Sessions",
        "text": (
            "MLflow Chat Sessions 화면은 trace metadata의 mlflow.trace.session 값을 기준으로 "
            "같은 대화의 여러 turn을 묶어서 보여준다."
        ),
    },
    {
        "id": "rag_role",
        "title": "RAG와 Dataset 차이",
        "text": (
            "MLflow Dataset은 평가용 질문과 기대값을 저장하는 문제집 역할이다. "
            "RAG 검색 저장소는 질문과 관련된 문서를 찾아 LLM 프롬프트에 추가하는 지식창고 역할이다."
        ),
    },
]
