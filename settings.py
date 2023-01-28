import os

BASE_URL = "https://api.soundingots.com"
ROOT_DIR = os.getenv("ABCTL_ROOT_DIR") or "~/.abctl"
USER_FILE = os.path.join(ROOT_DIR, "user")
WORKDIR_FILE = os.path.join(ROOT_DIR, "workdir")
WORKDIR_SUBDIRS = ["raw_out", "in", "out"]
