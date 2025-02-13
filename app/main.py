from fastapi import FastAPI
from app.api.endpoints import users, tweets, follows

app = FastAPI(title="Microblog API")

@app.get("/")
async def root():
    return {"message": "Microblog API is running!"}

app.include_router(users.router)
app.include_router(tweets.router)
app.include_router(follows.router)