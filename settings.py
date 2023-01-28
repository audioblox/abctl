import os

BASE_URL = "https://api.soundingots.com"
ROOT_DIR = os.getenv("ABCTL_ROOT_DIR") or "~/.abctl"
USER_FILE = os.path.join(ROOT_DIR, "user")
