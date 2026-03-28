import os

import gdown

# Create directory
os.makedirs("recommender", exist_ok=True)

MOVIES_ID = "1F5SenFGD0HXtZzo1H6AZkXWUS4Yab7Yp"
SIMILARITY_ID = "18caxCr4BLi1Bw_uu8EoEZ5uAcoe4pNEH"


def download(file_id, output):
    if os.path.exists(output):
        print(f"{output} already exists")
        return

    print(f"Downloading {output}...")
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output, quiet=False)


download(MOVIES_ID, "recommender/movies.pkl")
download(SIMILARITY_ID, "recommender/similarity.pkl")
