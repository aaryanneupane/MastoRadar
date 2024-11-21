from typing import Union
from mastodon import Mastodon
from fastapi import FastAPI, HTTPException
from src.DataFetcher import DataFetcher
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

mastodon = Mastodon(
    access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
    api_base_url=os.getenv("MASTODON_API_BASE_URL")
)

data = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/setApi")
def setApi(baseUrl: str, token: str):
    global mastodon
    try:
        mastodon = Mastodon(
            access_token=token,
            api_base_url=baseUrl
        )
        mastodon.account_verify_credentials()
        global data
        data = DataFetcher(mastodon)
        return {"message": "Successfully connected to API"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect to API: {e}")

@app.get("/getSuggestedUsers")
def getSuggestedUsers():
    return mastodon.suggestions()

@app.get("/getPublicTimeline")
def getPublicTimeline(pageNumber: int):
    return len(mastodon.timeline_public())

