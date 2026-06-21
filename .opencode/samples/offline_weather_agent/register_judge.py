"""기존 Judge/Scorer 실행 경로를 유지하기 위한 호환 wrapper."""

from entrypoints.register_judge import main


if __name__ == "__main__":
    main()
