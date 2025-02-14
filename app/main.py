from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.endpoints import users, tweets, follows

app = FastAPI(title="Microblog API", redirect_slashes=True)

app.include_router(users.router)
app.include_router(tweets.router)
app.include_router(follows.router)

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
