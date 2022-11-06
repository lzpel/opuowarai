import os
import json


def get_path(filename):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)


def main():
    with \
            open(get_path('Pipfile'), "r") as fp, \
            open(get_path('Pipfile.lock'), "r") as fl, \
            open(get_path("requirements.txt"), "w") as fr:
        json_fl = json.load(fl)
        text_fp = fp.read()
        for name, pkg in json_fl["default"].items():
            if name in text_fp:
                print(name, pkg["version"], file=fr, sep="")


if __name__ == "__main__":
    main()