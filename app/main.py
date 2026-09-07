from fastapi import FastAPI
from app import models
from app.database import engine
from app.routes import auth, feed, follows, likes, post_media, posts, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def helloAPI():
    return {"message": "FeedAPI running!"}

app.include_router(posts.router)
app.include_router(post_media.router)
app.include_router(follows.router)
app.include_router(likes.router)
app.include_router(feed.router)
app.include_router(auth.router)
app.include_router(users.router)
