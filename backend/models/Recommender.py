import numpy as np
import random
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
from .Embeddings import EmbeddingModel
from utils.preprocessing import parse_mastodon_post
from mastodon import Mastodon


class Recommender:
    def __init__(self, mastodon: Mastodon):
        self.mastodon = mastodon
        self.embeddingModel = EmbeddingModel()
        self.embedding_cache = {}

    def get_similar_posts(self, limit=1000, top_n=40):
        # Fetch favorited posts
        favorited_posts = self.mastodon.favourites()

        # Fetch and filter public posts
        public_posts = self._fetch_public_posts(limit)
        public_posts = self._filter_posts(public_posts)

        # Generate embeddings for favorited and public posts
        favorite_embeddings = self._generate_favorite_embeddings(favorited_posts)
        public_embeddings = self._generate_public_embeddings(public_posts)

        # Compute similarities and return recommendations
        recommendations = self._compute_similarities(favorite_embeddings, public_embeddings)
        top_recommendations = recommendations[:top_n]
        # Randomness for diversity
        for _ in range(4):
            random_recommendation = np.random.choice(recommendations)
            top_recommendations.append(random_recommendation)
        return random.shuffle(top_recommendations)

    def _fetch_public_posts(self, limit):
        posts = []
        max_id = None
        while len(posts) < limit:
            batch = self.mastodon.timeline_local(max_id=max_id, limit=min(40, limit - len(posts)))
            if not batch:
                break
            posts.extend(batch)
            max_id = batch[-1]["id"]
        return posts

    def _filter_posts(self, posts):
        seen_content = set()
        return [
            post for post in posts
            if post.get("language", None) == "en" and post.get("content", "").strip() not in seen_content
        ]

    def _generate_favorite_embeddings(self, favorited_posts):
        return [
            self._get_or_compute_embedding(post)
            for post in favorited_posts if self._get_or_compute_embedding(post) is not None
        ]

    def _generate_public_embeddings(self, public_posts):
        with ThreadPoolExecutor(max_workers=8) as executor:
            return list(executor.map(
                lambda post: (post, self._get_or_compute_embedding(post)),
                public_posts
            ))

    def _get_or_compute_embedding(self, post):
        post_id = post["id"]
        if post_id in self.embedding_cache:
            return self.embedding_cache[post_id]

        data = parse_mastodon_post(post)
        text_emb = self.embeddingModel.generate_text_embedding(data["text"]) if data["text"] else None
        img_embs = [self.embeddingModel.generate_image_embedding(url) for url in data["media_urls"]]
        combined_emb = self._combine_embeddings(text_emb, img_embs)

        self.embedding_cache[post_id] = combined_emb
        return combined_emb

    def _combine_embeddings(self, text_embedding=None, image_embeddings=[]):
        embeddings = []
        if text_embedding is not None:
            embeddings.append(text_embedding / np.linalg.norm(text_embedding))
        embeddings.extend(img / np.linalg.norm(img) for img in image_embeddings if np.linalg.norm(img) > 0)
        return np.mean(embeddings, axis=0) if embeddings else None

    def _compute_similarities(self, favorite_embeddings, public_embeddings):
        public_data = [(post, emb) for post, emb in public_embeddings if emb is not None]
        public_posts, public_embeds = zip(*public_data) if public_data else ([], [])
        public_embeds = np.array(public_embeds)

        scores = cosine_similarity(public_embeds, favorite_embeddings).mean(axis=1)
        recommendations = sorted(zip(public_posts, scores), key=lambda x: x[1], reverse=True)
        return [post for post, _ in recommendations]
