from typing import Union
from mastodon import Mastodon
from fastapi import FastAPI, HTTPException, Query
from src.DataFetcher import DataFetcher
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from models.Recommender import Recommender
import numpy as np

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

recommender = Recommender(mastodon)

def numpy_to_python(obj):
    """
    Recursively convert numpy types to Python types for JSON serialization.
    """
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()  # Converts numpy int/float to Python int/float
    elif isinstance(obj, np.ndarray):
        return obj.tolist()  # Converts numpy array to list
    elif isinstance(obj, dict):
        return {key: numpy_to_python(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [numpy_to_python(value) for value in obj]
    return obj


@app.get("/")
def read_root():
    return {"message": "Welcome to Mastodon Recommender API!"}

@app.get("/getRecommendations")
def getRecommendations():
    """
    Fetch similar posts based on the user's favorites.
    :param top_n: Number of recommendations to return.
    :param limit: Number of public posts to analyze.
    :return: List of recommended posts.
    """
    try:
        recommendations = recommender.get_similar_posts()
        safe_recommendations = numpy_to_python(recommendations)
        return safe_recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


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

@app.get("/getFavourites")
def getFavourites():
    return mastodon.favourites()


# HOW TO FETCH THE EXPLORE TIMELINE (FORMATED AS A JSON OBJECT)
# fetch('https://mastodon.social/api/v1/trends/statuses', {
#         headers: {
#             Authorization: `Bearer B-INjGrQDnTIti8QMazyOWcabEvw8g_D_G2Pc0nJ04I`,
#         },
#     })
#     .then((response) => response.json())
#     .then((data) => console.log(data))
#     .catch((error) => console.error(error));