"""기존 LangChain 실행 경로를 유지하기 위한 호환 wrapper."""

from entrypoints.langchain_agent import main


if __name__ == "__main__":
    main()
