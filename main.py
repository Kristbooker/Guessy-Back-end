import random
from fastapi import FastAPI, HTTPException, Depends , status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Annotated,Optional

from gensim.models import Word2Vec
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')

import models
from database import engine,SessionLocal
from sqlalchemy.orm import Session



app = FastAPI()

models.Base.metadata.create_all(bind=engine)

class UserBase(BaseModel):
    id: int
    username: str
    email : str
    exp : float
    coins : int
    profileImage : str
    winStat : int
    loseStat : int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# db_dependency =  Annotated(Session, Depends(get_db))

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    


model_path = "/Users/krist/Guessy/GuessyServer/guessyModel.model"
model = Word2Vec.load(model_path)

class Guess(BaseModel):
    answerWord: str
    guessWord: str

class Hint(BaseModel):
    answerWord: str
    highestRank: int

class Top(BaseModel):
    answerWord: str

def check_word(word):
    stop_words = set(stopwords.words('english'))
    lemma = WordNetLemmatizer()
    lemma_word = lemma.lemmatize(word.lower())
    if lemma_word in stop_words:
        raise HTTPException(status_code=404, detail="Word not found")
    return lemma_word

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/gettop")
def get_top(top: Top):
    answerWord = top.answerWord
    similar_words = model.wv.most_similar(answerWord, topn=10)
    return {"top 10": similar_words}

@app.post("/hint")
def hint_word(hint: Hint):
    answerWord = hint.answerWord
    highestRank = hint.highestRank - 2
    if highestRank <= 0:
        return {"hint": "You can't get more hint!"}
    elif highestRank > 300:
        highestRank = 300

    similar_words = model.wv.most_similar(answerWord, topn=highestRank)
    rankTarget = random.randint(0, len(similar_words) - 1)

    if 0 <= rankTarget < len(similar_words):
        target_word = similar_words[rankTarget][0]
        return {"hint": target_word, "rank": rankTarget + 2}
    else:
        return {"hint": "Rank out of range"}

@app.post("/guessy")
def guessy(guess: Guess):
    answerWord = guess.answerWord
    guessWord = guess.guessWord
    gWord = check_word(guessWord)
    rank = model.wv.rank(answerWord, gWord)
    if answerWord == gWord:
        return {"gWord": gWord, "rank": rank, "status": "win", "color": "#84cf63"}
    else:
        if rank < 300:
            return {"gWord": gWord, "rank": rank + 1, "status": "lose", "color": "#84cf63"}
        elif rank < 1500:
            return {"gWord": gWord, "rank": rank + 1, "status": "lose", "color": "#f0b911"}
        else:
            return {"gWord": gWord, "rank": rank + 1, "status": "lose", "color": "#d55c5c"}


