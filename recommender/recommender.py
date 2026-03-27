import ast

import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@st.cache_resource
def load_model():
    movies = pd.read_csv("tmdb_5000_movies.csv")
    credits = pd.read_csv("tmdb_5000_credits.csv")
    movies = movies.merge(credits, on="title")

    movies = movies[
        ["movie_id", "title", "overview", "genres", "keywords", "cast", "crew"]
    ].dropna()

    def convert(text):
        return [i["name"] for i in ast.literal_eval(text)]

    def convert_cast(text):
        return [i["name"] for i in ast.literal_eval(text)[:3]]

    def fetch_director(text):
        for i in ast.literal_eval(text):
            if i["job"] == "Director":
                return [i["name"]]
        return []

    movies["genres"] = movies["genres"].apply(convert)
    movies["keywords"] = movies["keywords"].apply(convert)
    movies["cast"] = movies["cast"].apply(convert_cast)
    movies["crew"] = movies["crew"].apply(fetch_director)
    movies["overview"] = movies["overview"].apply(lambda x: x.split())

    for col in ["genres", "keywords", "cast", "crew"]:
        movies[col] = movies[col].apply(lambda x: [i.replace(" ", "") for i in x])

    movies["tags"] = (
        movies["overview"]
        + movies["genres"]
        + movies["keywords"]
        + movies["cast"]
        + movies["crew"]
    )
    movies["tags"] = movies["tags"].apply(lambda x: " ".join(x))

    cv = CountVectorizer(max_features=5000, stop_words="english")
    vectors = cv.fit_transform(movies["tags"]).toarray()
    similarity = cosine_similarity(vectors)

    return movies, similarity


def recommend(movie_title, k=5):
    movies, similarity = load_model()
    index = movies[movies["title"] == movie_title].index[0]

    distances = sorted(
        list(enumerate(similarity[index])), key=lambda x: x[1], reverse=True
    )

    return [movies.iloc[i[0]].title for i in distances[1 : k + 1]]
