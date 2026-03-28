import os

import requests


def download_file(url, filename):
    if os.path.exists(filename):
        print(f"{filename} already exists")
        return

    print(f"Downloading {filename}...")
    r = requests.get(url)
    with open(filename, "wb") as f:
        f.write(r.content)
    print(f"{filename} downloaded!")


# 🔥 PUT YOUR LINKS HERE
MOVIES_URL = (
    "https://drive.google.com/file/d/1F5SenFGD0HXtZzo1H6AZkXWUS4Yab7Yp/view?usp=sharing"
)
SIMILARITY_URL = (
    "https://drive.google.com/file/d/18caxCr4BLi1Bw_uu8EoEZ5uAcoe4pNEH/view?usp=sharing"
)

download_file(MOVIES_URL, "movies.pkl")
download_file(SIMILARITY_URL, "similarity.pkl")
