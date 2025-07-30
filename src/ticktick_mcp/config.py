import argparse
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# --- Configuration --- (Argument Parsing and Directory/File Handling)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%((asctime)s)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

# Required credentials
REQUIRED = [
    "TICKTICK_CLIENT_ID",
    "TICKTICK_CLIENT_SECRET",
    "TICKTICK_REDIRECT_URI",
    "TICKTICK_USERNAME",
    "TICKTICK_PASSWORD"
]

# Setup argument parser for optional dotenv-dir flag
parser = argparse.ArgumentParser(
    description="Run the TickTick MCP server, optionally specifying the directory for the .env file."
)
parser.add_argument(
    "--dotenv-dir",
    type=str,
    help="Path to the directory containing the .env file. If omitted and all credentials are in the environment, no .env is loaded."
)
args = parser.parse_args()

# Check if all required credentials are already set in environment
env_complete = all(os.getenv(k) for k in REQUIRED)

if env_complete and args.dotenv_dir is None:
    logging.info("All required environment variables found; skipping .env loading.")
else:
    # Determine target directory for .env (explicit or default)
    dotenv_dir = Path(args.dotenv_dir or "~/.config/ticktick-mcp").expanduser()
    # Ensure directory exists
    try:
        dotenv_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Ensured directory exists: {dotenv_dir}")
    except OSError as e:
        logging.error(f"Error creating directory {dotenv_dir}: {e}")
        sys.exit(1)
    # Path to .env
    dotenv_path = dotenv_dir / ".env"
    # If credentials missing, require .env file
    if not env_complete and not dotenv_path.is_file():
        logging.error(f"Required .env file not found at {dotenv_path}")
        logging.error("Please create the .env file with your TickTick credentials.")
        logging.error("Expected content:")
        logging.error("  TICKTICK_CLIENT_ID=your_client_id")
        logging.error("  TICKTICK_CLIENT_SECRET=your_client_secret")
        logging.error("  TICKTICK_REDIRECT_URI=your_redirect_uri")
        logging.error("  TICKTICK_USERNAME=your_ticktick_email")
        logging.error("  TICKTICK_PASSWORD=your_ticktick_password")
        sys.exit(1)
    # Load .env if file exists (regardless of explicit)
    loaded = load_dotenv(override=True, dotenv_path=dotenv_path)
    if loaded:
        logging.info(f"Loaded environment variables from: {dotenv_path}")
    else:
        if dotenv_path.is_file():
            logging.error(f"Failed to load environment variables from {dotenv_path}")
            sys.exit(1)
        else:
            # This branch when env_complete but user passed --dotenv-dir but file missing
            logging.info(f"No .env file at {dotenv_path}; relying on environment variables.")

# --- Environment Variable Loading --- #
CLIENT_ID     = os.getenv("TICKTICK_CLIENT_ID")
CLIENT_SECRET = os.getenv("TICKTICK_CLIENT_SECRET")
REDIRECT_URI  = os.getenv("TICKTICK_REDIRECT_URI")
USERNAME      = os.getenv("TICKTICK_USERNAME")
PASSWORD      = os.getenv("TICKTICK_PASSWORD")
