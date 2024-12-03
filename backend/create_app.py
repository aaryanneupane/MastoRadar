from mastodon import Mastodon

#Not to be used on each run, app creation should be done once, then the client_id and client_secret should be stored in the .env file
Mastodon = Mastodon.create_app(
"MastoRadar",
scopes=['read', 'write', 'follow', 'push'],
redirect_uris="http://127.0.0.1:8000/callback",
website="http://127.0.0.1:8000",
to_file=None,
api_base_url='https://mastodon.social',
request_timeout=300,
session=None,
user_agent='mastodonpy')

print(Mastodon)