from fastapi import FastAPI
from app.api.endpoints import users, tweets

app = FastAPI(title="Microblog API")

@app.get("/")
def root():
    return {"message": "Microblog API is running!"}


app = FastAPI(title="Microblog API")

app.include_router(users.router)
app.include_router(tweets.router)
