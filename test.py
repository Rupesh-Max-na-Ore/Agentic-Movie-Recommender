import pickle

movies = pickle.load(open("recommender/movies.pkl", "rb"))

print(movies.columns)
print(movies.iloc[0])
