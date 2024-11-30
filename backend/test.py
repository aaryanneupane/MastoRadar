from typing import Union
from mastodon import Mastodon
from fastapi import FastAPI, HTTPException, Query
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from models.Recommender import Recommender

load_dotenv()

mastodon = Mastodon(
    access_token=os.getenv("MASTODON_ACCESS_TOKEN"),
    api_base_url=os.getenv("MASTODON_API_BASE_URL")
)

recommender = Recommender(mastodon)

def getRecommendations():
    """
    Fetch similar posts based on the user's favorites.
    :param top_n: Number of recommendations to return.
    :param limit: Number of public posts to analyze.
    :return: List of recommended posts.
    """
    recommendations = recommender.get_similar_posts()
    return {"recommendations": recommendations}

print(getRecommendations())
