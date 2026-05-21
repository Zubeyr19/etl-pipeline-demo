import argparse
from src.logger import setup_logging
from src.pipeline import run_pipeline
from src.scheduler import start_scheduler

setup_logging()


def main():
    parser = argparse.ArgumentParser(description="Weather ETL Pipeline")
    parser.add_argument(
        "--mode",
        choices=["once", "schedule"],
        default="once",
        help="Run once or start the scheduler (default: once)",
    )
    args = parser.parse_args()

    if args.mode == "schedule":
        start_scheduler()
    else:
        result = run_pipeline()
        print(f"\nRun complete: {result}")


if __name__ == "__main__":
    main()
