from mastodon import Mastodon
import os
import secrets
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

MASTODON_CLIENT_ID = os.getenv("MASTODON_CLIENT_ID")
MASTODON_CLIENT_SECRET = os.getenv("MASTODON_CLIENT_SECRET")
MASTODON_API_BASE_URL = os.getenv("MASTODON_API_BASE_URL")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://127.0.0.1:8000/callback")

# Mastodon authentication handler
class AuthHandler:
    def __init__(self):
        self.mastodon = Mastodon(
            client_id=MASTODON_CLIENT_ID,
            client_secret=MASTODON_CLIENT_SECRET,
            api_base_url=MASTODON_API_BASE_URL,
        )

    def generate_auth_url(self):
        """
        Generate the Mastodon authorization URL for the login flow.
        """
        print(f"client_id: {MASTODON_CLIENT_ID}")
        state = secrets.token_urlsafe(16)  # Optional: Use for CSRF protection
        auth_url = self.mastodon.auth_request_url(
            client_id=MASTODON_CLIENT_ID,
            redirect_uris=REDIRECT_URI,
            scopes=["read", "write", "follow"],
            state=state,
        )
        return auth_url, state

    def exchange_code_for_token(self, code):
        """
        Exchange the authorization code for an access token.
        """
        access_token = self.mastodon.log_in(
            code=code,
            redirect_uri=REDIRECT_URI,
            scopes=["read", "write", "follow"],
        )
        return access_token
