from typing import Union
from mastodon import Mastodon
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
# from src.DataFetcher import DataFetcher
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
import httpx

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

unauthorized_mastodon = Mastodon(
    client_id=os.getenv("MASTODON_CLIENT_ID"),
    client_secret=os.getenv("MASTODON_CLIENT_SECRET"),
    api_base_url=os.getenv("MASTODON_API_BASE_URL")
)

data = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/login")
def login():
    # Redirect the user to the Mastodon authorization page
    auth_url = unauthorized_mastodon.auth_request_url(
        client_id=os.getenv("MASTODON_CLIENT_ID"),
        redirect_uris='http://127.0.0.1:8000/callback',
        scopes=['read', 'write','follow'],
        #should add a random state
    )
    print(f"Authorization URL: {auth_url}")  # Debug print statement
    return auth_url

@app.get("/callback")
async def callback(request: Request):
    # Get the authorization code from the callback URL
    code = request.query_params.get('code')
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")

    print(f"Authorization code before: {code}")  # Debug print statement
    access_token = unauthorized_mastodon.log_in(
        code=code,
        redirect_uri='http://127.0.0.1:8000/callback',
        scopes=['read', 'write','follow']
    )
    print(f"Access code after: {access_token}")  # Debug print statement
    
    global mastodon
    mastodon = Mastodon(
    access_token=access_token,
    api_base_url=os.getenv("MASTODON_API_BASE_URL")
    )

    return RedirectResponse(url="http://localhost:5173/")


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

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

@app.get("/getRecommendedTimeline")
async def get_explore_timeline():
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get('http://192.168.86.157:8000/getRecommendations')
        return response.json()

# API for explore page:
# 'https://mastodon.social/api/v1/trends/statuses'
