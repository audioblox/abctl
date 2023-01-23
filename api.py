import os
import sys
import json
import requests
import settings

from typing import Dict


def read_userfile(verbose=False) -> Dict:
    if verbose:
        print("\n----------")
        print("\nread_userfile")

    file_path = os.getenv("ABCTLCONFIG")
    if verbose:
        print("\nReading userfile from:", file_path)

    if not os.path.exists(file_path):
        if verbose:
            print("\nFile does not exist")
        return {}

    f = open(file_path, "r")
    user = json.loads(f.read())
    f.close()
    if verbose:
        print("\nRead file, returning:", user)
        print("\n==========")
    return user


def get_url(url: str) -> str:
    return "%s/%s/" % (settings.BASE_URL, url)


class Api:
    def __update__file__(refresh: str, access: str, me: Dict, verbose=False):
        if verbose:
            print("\n----------")
            print("\nApi.__update_file__")

        tokens = {
            "refresh": refresh,
            "access": access,
        }
        user = {
            **tokens,
            **me,
        }

        if verbose:
            print("\nFile contents:", user)

        f = open(os.getenv("ABCTLCONFIG"), "w+")
        f.write(json.dumps(user))
        f.close()

        if verbose:
            print("\nClosed file")
            print("\n==========")

        return

    @classmethod
    def __authenticate__(self, verbose=False):
        if verbose:
            print("\n----------")
            print("\nApi.__authenticate__")

        user = read_userfile(verbose)

        if verbose:
            print("\nUser from file:", user)

        if "refresh" not in user or "access" not in user:
            if verbose:
                print("\nTokens not found in user file.")
            print("You are not logged in")
            try:
                os.remove(os.getenv("ABCTLCONFIG"))
            except Exception:
                pass

            sys.exit(401)

        headers = {"Authorization": "Bearer %s" % user["access"]}
        if verbose:
            print("\nAuthorization header:", "Bearer %s" % user["access"][0:10])

        res = requests.get(get_url("account/me"), headers=headers)

        if verbose:
            print("\nAccount response:", res.status_code, res.text)

        if res.status_code == 200:
            self.__update__file__(
                user["refresh"], user["access"], json.loads(res.text), verbose
            )
            if verbose:
                print("\nReturning", res.text)

            return res

        if verbose:
            print("\nRefreshing token...")

        access = json.loads(
            requests.post(
                get_url("account/token/refresh"), {"refresh": user["refresh"]}
            ).text
        )["access"]

        if verbose:
            print("\nNew access token:", access[0:10])

        headers = {"Authorization": "Bearer %s" % access}
        res = requests.get(get_url("account/me"), headers=headers)

        if verbose:
            print("\nResponse:", res.status_code, res.text)

        if res.status_code != 200:
            print("You are not logged in")
            try:
                os.remove(os.getenv("ABCTLCONFIG"))
            except Exception:
                pass
            sys.exit(res.status_code)

        self.__update__file__(user["refresh"], access, json.loads(res.text))

        if verbose:
            print("\nReturning", res)
            print("\n==========")

        return res

    @classmethod
    def __get__(self, url: str, auth_required=True):
        if auth_required:
            self.__authenticate__()

        return requests.get(get_url(url))

    @classmethod
    def __post__(self, url: str, payload: Dict, auth_required=True):
        if auth_required:
            self.__authenticate__()

        return requests.post(get_url(url), payload)

    @classmethod
    def me(self, verbose=False) -> requests.Response:
        if verbose:
            print("\n----------")
            print("\nApi.me")
        result = self.__authenticate__(verbose)
        if verbose:
            print("\nReturning:", result)
            print("\n==========")
        return result

    @classmethod
    def login(self, email: str, password: str) -> requests.Response:
        payload = {
            "email": email,
            "password": password,
        }
        return self.__post__("account/token", payload, auth_required=False)
