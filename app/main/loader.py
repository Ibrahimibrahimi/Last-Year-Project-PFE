# load data from json files


import os  # to know how mmuch langages e have
import json

langs = os.listdir("app/data")
data = [
    {i: json.load(f"app/data/{i}")} for i in os.listdir("app/data")
]

stats = {
    "langs_count":len(langs),
    "langs":langs
}