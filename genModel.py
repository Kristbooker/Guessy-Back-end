import gensim.downloader as api
from gensim.models import Word2Vec

dataset = api.load("text8")
# model2 = Word2Vec.load('guessyModel.model')
model = Word2Vec(dataset, vector_size=100, window=5, min_count=1, workers=4)

# similar_word2 = model2.wv.most_similar("apple")
# print(similar_word2)
model.save("guessyModel.model")