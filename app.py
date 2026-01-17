"""
StudyBuddy AI - SDG 4: Quality Education
Entry point for the Streamlit application.
"""

# Load .env file early (though controller will reload it in Streamlit context)
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
# Try project root first, then utils folder as fallback
ENV_PATH = BASE_DIR / ".env"
if not ENV_PATH.exists():
    ENV_PATH = BASE_DIR / "utils" / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=False)

# Import controller after .env is loaded
from backend.controller import run_app


def main() -> None:
    """Main function that runs the StudyBuddy AI app."""
    run_app()


if __name__ == "__main__":
    main()
