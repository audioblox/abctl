import os
import sys
import json
import requests
import settings

from typing import Dict
from utils import hash_file_content


def read_userfile(verbose=False) -> Dict:
    if verbose:
        print("\n----------")
        print("\nread_userfile")

    file_path = settings.USER_FILE
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

        f = open(settings.USER_FILE, "w+")
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
                os.remove(settings.USER_FILE)
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
                os.remove(settings.USER_FILE)
            except Exception:
                pass
            sys.exit(res.status_code)

        self.__update__file__(user["refresh"], access, json.loads(res.text))

        if verbose:
            print("\nReturning", res)
            print("\n==========")

        return res

    def __get_headers__(auth_required: bool):
        if not auth_required:
            return
        user = read_userfile()
        return {"Authorization": "Bearer %s" % user["access"]}

    @classmethod
    def __get__(self, url: str, auth_required=True):
        if auth_required:
            self.__authenticate__()

        headers = self.__get_headers__(auth_required=auth_required)
        return requests.get(get_url(url), headers=headers)

    @classmethod
    def __post__(self, url: str, payload: Dict, files: str = None, auth_required=True):
        if auth_required:
            self.__authenticate__()

        headers = self.__get_headers__(auth_required=auth_required)
        return requests.post(get_url(url), payload, files=files, headers=headers)

    @classmethod
    def login_check(self):
        return self.__authenticate__()

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

    @classmethod
    def upload_file(self, file_path: str, subdir: str):
        name = os.path.basename(file_path)
        print("Preparing %s/%s for upload" % (subdir, name))
        size = os.path.getsize(file_path)
        hash = hash_file_content(file_path=file_path)

        # Check if file already exists
        res = self.__get__("audio_file/existing_source_file/%i/%s" % (size, hash))
        if res.status_code == 200:
            print("%s already exists. File uuid:\n%s" % (name, res.json()["file_uuid"]))
            return False

        # Upload the file
        print("Uploading %s..." % name)
        file = open(file_path, "rb")
        files = {
            "file_0": file,
        }
        payload = {
            "file_0_modified": os.path.getmtime(file_path),
            "file_0_is_source": "True",
        }
        res = self.__post__(
            "audio_file/audio_files",
            payload,
            files=files,
        )
