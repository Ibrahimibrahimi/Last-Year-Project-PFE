# load data from json files


import os  # to know how mmuch langages e have
import json
import glob


langs = os.listdir("app/data")


def load_all_languages() -> list[dict]:
    """
    Scan ./data for every *.json file and return a list of language objects,
    sorted by the 'id' field.  Each file is expected to follow the schema
    illustrated by python.json.
    """
    languages = []
    pattern = os.path.join("/data", "*.json")
    for path in sorted(glob.glob(pattern)):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            languages.append(data)
        except (json.JSONDecodeError, OSError) as exc:
            print("==================== ERROR JSON ==================")
    return languages
