from typing import Union
from mastodon import Mastodon
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
import httpx
from auth import AuthHandler

load_dotenv()

app = FastAPI()
auth_handler = AuthHandler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

authenticated = False
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
    #Generate the Mastodon authorization URL and redirect the user to it.
    auth_url, state = auth_handler.generate_auth_url()
    # print(f"Authorization URL: {auth_url}")  # Debugging
    return auth_url

@app.get("/callback")
async def callback(request: Request):
    #Handle the Mastodon OAuth2 callback and exchange the authorization code for an access token.
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found")

    try:
        access_token = auth_handler.exchange_code_for_token(code)
        # print(f"Access token: {access_token}")  # Debugging

        global mastodon
        mastodon = Mastodon(
        access_token=access_token,
        api_base_url=os.getenv("MASTODON_API_BASE_URL")
        )
        global authenticated
        authenticated = True

        redirect_url = f"http://localhost:5173/authenticated?access_token={access_token}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@app.get("/getuser")
async def getUser(request: Request):
    access_token = request.query_params.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Access token is required")

    mastodon = Mastodon(
        access_token=access_token,
        api_base_url=os.getenv("MASTODON_API_BASE_URL")
    )
    user = mastodon.account_verify_credentials()
    global authenticated
    authenticated = True

    user_id = user.get("id")
    username = user.get("username")
    display_name = user.get("display_name")

    # Return the extracted user data
    return {
        "user_id": user_id,
        "username": username,
        "display_name": display_name
    }

@app.post("/logout")
def logout():
    global authenticated
    authenticated = False
    return {"message": "Logged out successfully"}

@app.get("/getPublicTimeline")
def getPublicTimeline():
    return unauthorized_mastodon.timeline_public()

@app.get("/getLocalTimeline")
def getLocalTimeline():
    return unauthorized_mastodon.timeline_local()

@app.get("/getHomeTimeline")
def getHomeTimeline():
  if authenticated:
    return mastodon.timeline_home()
  else:
    raise HTTPException(status_code=400, detail="Not authenticated")

@app.get("/getRecommendedTimeline")
async def getRecommendedTimeline():
  if authenticated:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get('http://192.168.86.157:8000/getRecommendations')
        return response.json()
  else:
    raise HTTPException(status_code=400, detail="Not authenticated")

# API for explore page:
# 'https://mastodon.social/api/v1/trends/statuses'
