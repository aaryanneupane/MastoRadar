from typing import Union
from mastodon import Mastodon
from fastapi import FastAPI, HTTPException
from src.DataFetcher import DataFetcher
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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
def setApi():
    global mastodon
    try:  
        mastodon.app_verify_credentials()
        global data
        data = DataFetcher(mastodon)
        return {"message": "Successfully connected to API"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to connect to API: {e}")

# @app.get("/getSuggestedUsers")
# def getSuggestedUsers():
#     return mastodon.suggestions()

@app.get("/getPublicTimeline")
def getPublicTimeline():
    return mastodon.timeline_public()

@app.get("/getHomeTimeline")
def getHomeTimeline():
    return mastodon.timeline_home() 

@app.get("/getLocalTimeline")
def getLocalTimeline():
    return mastodon.timeline_local()

# HOW TO FETCH THE EXPLORE TIMELINE (FORMATED AS A JSON OBJECT)
# fetch('https://mastodon.social/api/v1/trends/statuses', {
#         headers: {
#             Authorization: `Bearer B-INjGrQDnTIti8QMazyOWcabEvw8g_D_G2Pc0nJ04I`,
#         },
#     })
#     .then((response) => response.json())
#     .then((data) => console.log(data))
#     .catch((error) => console.error(error));