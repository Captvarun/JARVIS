import sys
from app.bootstrap import bootstrap
from app.app import run_app

def main():
    """
    JARVIS Application Entry Point.
    """
    bootstrap()
    run_app()

if __name__ == "__main__":
    main()
