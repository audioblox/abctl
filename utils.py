import getpass

from typing import Callable
from validators import (
    validate_email,
    validate_password,
)


def get_input(label: str, secure=False, validate: Callable = None):
    user_intput = None
    if secure:
        user_intput = getpass.getpass(label)
    else:
        user_intput = input(label)

    if validate:
        error = validate(user_intput)
        if len(error) > 0:
            print("%s\n" % error)
            return get_input(label, secure, validate)

    return user_intput


def get_email():
    return get_input("Enter email:\t", validate=validate_email)


def get_password():
    return get_input("Enter password:\t", validate=validate_password, secure=True)
