import os
import sys
import json
import requests
import settings

from typing import Dict


def read_userfile() -> Dict:
    file_path = settings.USER_FILE
    if not os.path.exists(file_path):
        return {}

    f = open(file_path, "r")
    user = json.loads(f.read())
    f.close()
    return user


def get_url(url: str) -> str:
    return "%s/%s/" % (settings.BASE_URL, url)


class Api:
    def __update__file__(refresh: str, access: str, me: Dict):
        tokens = {
            "refresh": refresh,
            "access": access,
        }
        f = open(settings.USER_FILE, "w")
        f.write(
            json.dumps(
                {
                    **tokens,
                    **me,
                }
            )
        )
        f.close()
        return

    @classmethod
    def __authenticate__(self):
        user = read_userfile()
        if "refresh" not in user or "access" not in user:
            print("You are not logged in")
            try:
                os.remove(settings.USER_FILE)
            except Exception:
                pass

            sys.exit(401)

        headers = {"Authorization": "Bearer %s" % user["access"]}

        res = requests.get(get_url("account/me"), headers=headers)
        if res.status_code == 200:
            self.__update__file__(user["refresh"], user["access"], json.loads(res.text))
            return res

        access = json.loads(
            requests.post(
                get_url("account/token/refresh"), {"refresh": user["refresh"]}
            ).text
        )["access"]
        headers = {"Authorization": "Bearer %s" % access}
        res = requests.get(get_url("account/me"), headers=headers)

        if res.status_code != 200:
            print("You are not logged in")
            try:
                os.remove(settings.USER_FILE)
            except Exception:
                pass
            sys.exit(res.status_code)

        self.__update__file__(user["refresh"], access, json.loads(res.text))

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
    def me(self) -> requests.Response:
        return self.__authenticate__()

    @classmethod
    def login(self, email: str, password: str) -> requests.Response:
        payload = {
            "email": email,
            "password": password,
        }
        return self.__post__("account/token", payload, auth_required=False)
