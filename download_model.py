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
MOVIES_URL = "https://drive.google.com/uc?id=1F5SenFGD0HXtZzo1H6AZkXWUS4Yab7Yp"
SIMILARITY_URL = "https://drive.google.com/uc?id=18caxCr4BLi1Bw_uu8EoEZ5uAcoe4pNEH"

# Ensure directory exists
os.makedirs("recommender", exist_ok=True)

download_file(MOVIES_URL, "recommender/movies.pkl")
download_file(SIMILARITY_URL, "recommender/similarity.pkl")
