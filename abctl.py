import os
import typer
import getpass
import sys
import json
import settings

from typing import Callable

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

    f = open(settings.USER_FILE, "w")
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


if __name__ == "__main__":
    app()
