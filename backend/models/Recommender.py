import numpy as np
import re
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
        """
        Fetch and recommend similar posts based on user favorites.
        :param limit: Number of public posts to analyze.
        :param top_n: Number of recommendations to return.
        """
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
        return recommendations[:top_n]

    def _fetch_public_posts(self, limit):
        """
        Fetch public posts up to the given limit using pagination.
        """
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
        """
        Filter posts to ensure they are in English and do not contain duplicate content.
        """
        seen_content = set()
        filtered_posts = []
        for post in posts:
            content = post.get("content", "").strip()
            if post.get("language") == "en" and content and content not in seen_content:
                clean_content = self._remove_urls(content)
                if self._is_valid_english(clean_content):
                    seen_content.add(content)
                    filtered_posts.append(post)
        # Log filtered count for debugging
        print(f"Filtered posts count: {len(filtered_posts)}")
        return filtered_posts

    def _is_valid_english(self, text):
        """
        Check if a text is predominantly in English using heuristic rules.
        """
        if not text:
            return False
        english_ratio = sum(1 for char in text if char.isalpha() and char.isascii()) / len(text)
        return english_ratio > 0.5  # Relaxed to include more posts

    def _generate_favorite_embeddings(self, favorited_posts):
        """
        Generate embeddings for favorited posts.
        """
        embeddings = [
            self._get_or_compute_embedding(post)
            for post in favorited_posts if self._get_or_compute_embedding(post) is not None
        ]
        print(f"Generated {len(embeddings)} favorite embeddings")  # Debugging
        return embeddings

    def _generate_public_embeddings(self, public_posts):
        """
        Generate embeddings for public posts using parallel computation.
        """
        with ThreadPoolExecutor(max_workers=8) as executor:
            embeddings = list(executor.map(
                lambda post: (post, self._get_or_compute_embedding(post)),
                public_posts
            ))
        print(f"Generated {len(embeddings)} public embeddings")  # Debugging
        return embeddings

    def _get_or_compute_embedding(self, post):
        """
        Compute or retrieve cached embedding for a post.
        """
        post_id = post["id"]
        if post_id in self.embedding_cache:
            return self.embedding_cache[post_id]

        data = parse_mastodon_post(post)
        clean_text = self._remove_urls(data["text"]) if data["text"] else None

        # Generate embeddings
        text_emb = self.embeddingModel.generate_text_embedding(clean_text) if clean_text else None
        img_embs = [self.embeddingModel.generate_image_embedding(url) for url in data["media_urls"]]
        combined_emb = self._combine_embeddings(text_emb, img_embs)

        # Cache embedding
        self.embedding_cache[post_id] = combined_emb
        return combined_emb

    def _remove_urls(self, text):
        """
        Remove URLs from a text string.
        """
        return re.sub(r'http\S+', '', text).strip()

    def _combine_embeddings(self, text_embedding=None, image_embeddings=[]):
        """
        Combine text and image embeddings into a single vector.
        """
        embeddings = []
        if text_embedding is not None:
            embeddings.append(text_embedding / np.linalg.norm(text_embedding))
        embeddings.extend(img / np.linalg.norm(img) for img in image_embeddings if np.linalg.norm(img) > 0)
        return np.mean(embeddings, axis=0) if embeddings else None

    def _compute_similarities(self, favorite_embeddings, public_embeddings):
        """
        Compute cosine similarities between favorite and public embeddings.
        """
        public_data = [(post, emb) for post, emb in public_embeddings if emb is not None]
        public_posts, public_embeds = zip(*public_data) if public_data else ([], [])
        public_embeds = np.array(public_embeds)

        # Compute cosine similarity
        scores = cosine_similarity(public_embeds, favorite_embeddings).mean(axis=1)

        # Rank posts by similarity score
        recommendations = sorted(zip(public_posts, scores), key=lambda x: x[1], reverse=True)
        return [post for post, _ in recommendations]
