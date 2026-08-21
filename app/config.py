import os
from pathlib import Path
APP_NAME="AI Critical Infrastructure Predictive Maintenance"
APP_VERSION="1.0.0"
DATABASE_URL=os.getenv("DATABASE_URL","sqlite:///./data/maintenance.db")
MODEL_DIR=Path(os.getenv("MODEL_DIR","./models")); MODEL_DIR.mkdir(parents=True,exist_ok=True)
