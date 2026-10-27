"""Launch with the correct configuration directory and fixed shell assets."""

import os
from pathlib import Path
import sys

from .prepare_assets import prepare_assets

prepare_assets()
os.chdir(Path(__file__).resolve().parent)
from streamlit.web import cli  # noqa: E402

sys.argv = ["streamlit", "run", "streamlit_app.py", *sys.argv[1:]]
cli.main()
