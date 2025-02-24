from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.endpoints import follows, medias, tweets, users

app = FastAPI(title="Microblog API", redirect_slashes=True)

app.include_router(users.router)
app.include_router(tweets.router)
app.include_router(follows.router)
app.include_router(medias.router)

UPLOAD_DIR = "uploads"

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
