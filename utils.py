import getpass
import sys
import os
import settings

from typing import Callable
from validators import (
    validate_email,
    validate_password,
)


def get_input(label: str, secure=False, validate: Callable = None, value: str = None):
    user_input = value
    if user_input is None:
        if secure:
            user_input = getpass.getpass(label)
        else:
            user_input = input(label)

    if validate is not None:
        error = validate(user_input)
        if len(error) > 0:
            print("\n%s\n" % error)
            return get_input(label, secure, validate)

    return user_input


def get_email(value: str):
    return get_input("Enter email:\t", validate=validate_email, value=value)


def get_password(value: str):
    return get_input(
        "Enter password:\t", validate=validate_password, secure=True, value=value
    )


def confirm_input(question: str = "Continue anyway?"):
    answer = input("%s y/n\n" % question)
    if not answer.lower() in ["y", "yes"]:
        print("Aborted")
        sys.exit(0)
    print("")


def workspace_check():
    def abort():
        print("ERROR: No workspace configured")
        print("Run `abctl init --help` for more information")
        print("")
        print("Aborted")
        sys.exit(100)

    if not os.path.exists(settings.WORKDIR_FILE):
        abort()

    f = open(settings.WORKDIR_FILE, "r")
    configured_dir = f.read()
    f.close()
    if not os.path.exists(configured_dir):
        abort()

    for subdir in settings.WORKDIR_SUBDIRS:
        if not os.path.isdir(os.path.join(configured_dir, subdir)):
            os.makedirs(os.path.join(configured_dir, subdir))
    return configured_dir
