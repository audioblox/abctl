import typer
import getpass

from typing import Callable

from utils import (
    get_email,
    get_password,
)

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
def login():
    print("Login to SoundIngots.com")
    email = get_email()
    password = get_password()
    print("email", password)


@app.command()
def logout():
    print("BYE!")


if __name__ == "__main__":
    app()
