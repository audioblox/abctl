import os
import typer
import getpass
import sys
import json
import settings

from typing import Callable
from utils import confirm_input

from utils import (
    get_email,
    get_password,
)
from api import Api

app = typer.Typer()


def get_input(label: str, secure=False, validate: Callable = None):
    if secure:
        input = getpass.getpass(label)
    else:
        input = input(label)

    if validate:
        if not validate():
            return get_input(label, secure, validate)

    return input


@app.command()
def login(
    email: str = typer.Option(None, "--email", "-e", help="Your email address"),
    password: str = typer.Option(None, "--password", "-p", help="Your password"),
):
    """
    Log in with your email address and password.
    """
    e = get_email(email)
    p = get_password(password)
    res = Api.login(e, p)
    try:
        os.remove(settings.USER_FILE)
    except Exception:
        pass

    if res.status_code != 200:
        print("ERROR: Login failed")
        sys.exit(res.status_code)

    tokens = json.loads(res.text)

    f = open(settings.USER_FILE, "w+")
    f.write(json.dumps(tokens))
    f.close()

    user_res = Api.me()
    user = json.loads(user_res.text)
    print("Logged in as %s" % user["username"])


@app.command()
def logout():
    """
    Log out
    """
    try:
        os.remove(settings.USER_FILE)
        print("You have been logged out")
    except Exception:
        print("You are not logged in")
        pass


@app.command()
def status(verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose mode")):
    """
    Who you're logged in as
    """
    if verbose:
        print("\n----------")
        print("\nabctl.status")

    user_res = Api.me(verbose)

    if verbose:
        print("\nUser response received:", user_res.text)

    user = json.loads(user_res.text)

    if verbose:
        print("\nUser JSON:", user)

    print("Logged in as %s" % user["username"])


@app.command()
def init(
    dir: str = typer.Argument(".", help="The directory to initialize in"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Ignore any current configuration"
    ),
):
    """
    Initialize your workfolder in the current working directory
    """
    # get absolute workdir
    cwd = os.getcwd()
    if dir != ".":
        cwd = os.path.abspath(os.path.join(cwd, dir))

    # check if workdir already exists
    if os.path.exists(settings.WORKDIR_FILE) and not force:
        f = open(settings.WORKDIR_FILE, "r")
        current_dir = f.read()
        if os.path.isdir(current_dir) and current_dir != cwd:
            print("WARNING: Workspace already configured. Current workspace:")
            print(current_dir)
            print("")
            confirm_input()

    # breakpoint()
    if not os.path.isdir(cwd):
        os.makedirs(cwd)

    # warn if directory is not empty
    is_empty = True
    for f in os.listdir(cwd):
        if not f.startswith(".") and f not in settings.WORKDIR_SUBDIRS:
            is_empty = False
            print(f)
            break

    if not is_empty:
        print("WARNING: Directory not empty:")
        print(cwd)
        print("")
        confirm_input("Continue anyway? No data will be deleted.")

    # save workdir in settings.WORKDIR_FILE
    f = open(settings.WORKDIR_FILE, "w+")
    f.write(cwd)
    f.close()

    # create subdirs
    for subdir in settings.WORKDIR_SUBDIRS:
        if not os.path.isdir(os.path.join(cwd, subdir)):
            os.makedirs(os.path.join(cwd, subdir))

    print("Initialized workspace at:")
    print(cwd)


if __name__ == "__main__":
    if not os.path.isdir(settings.ROOT_DIR):
        os.makedirs(settings.ROOT_DIR)
    app()
