import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .Embeddings import EmbeddingModel
from utils.preprocessing import parse_mastodon_post
from mastodon import Mastodon


class Recommender:
    """
    Generates recommendations based on user's favorite posts and public timeline posts.
    """

    def __init__(self, mastodon: Mastodon):
        self.mastodon = mastodon
        self.embeddingModel = EmbeddingModel()

    def get_similar_posts(self):
        """
        Get similar posts based on user favorites.
        :param top_n: Number of recommendations to return.
        :param limit: Number of public posts to analyze.
        :return: A list of recommended posts with similarity scores.
        """
        # Fetch favorited posts and public timeline
        favorited_posts = self.mastodon.favourites()
        public_posts = self.mastodon.timeline_public()

        # Generate embeddings for favorited posts
        favorite_embeddings = []
        for post in favorited_posts:
            data = parse_mastodon_post(post)
            text_emb = (
                self.embeddingModel.generate_text_embedding(data["text"])
                if data["text"]
                else None
            )
            img_embs = [
                self.embeddingModel.generate_image_embedding(url)
                for url in data["media_urls"]
            ]
            combined_emb = self._combine_embeddings(text_emb, img_embs)
            if combined_emb is not None:
                favorite_embeddings.append(combined_emb)

        # Generate embeddings for public timeline
        public_embeddings = []
        for post in public_posts:
            data = parse_mastodon_post(post)
            text_emb = (
                self.embeddingModel.generate_text_embedding(data["text"])
                if data["text"]
                else None
            )
            img_embs = [
                self.embeddingModel.generate_image_embedding(url)
                for url in data["media_urls"]
            ]
            combined_emb = self._combine_embeddings(text_emb, img_embs)
            public_embeddings.append((post, combined_emb))

        # Compute similarity scores
        recommendations = self._compute_similarities(
            favorite_embeddings, public_embeddings
        )
        # return recommendations[:top_n]
        return recommendations[:10]

    def _combine_embeddings(self, text_embedding=None, image_embeddings=[]):
        """
        Combine text and image embeddings.
        :param text_embedding: Text embedding vector.
        :param image_embeddings: List of image embedding vectors.
        :return: Combined embedding vector.
        """
        embeddings = []
        if text_embedding is not None:
            embeddings.append(text_embedding)
        embeddings.extend(image_embeddings)
        return np.mean(embeddings, axis=0) if embeddings else None

    def _compute_similarities(self, favorite_embeddings, public_embeddings):
        """
        Compute similarity scores between favorite embeddings and public embeddings.
        :param favorite_embeddings: List of embeddings for favorited posts.
        :param public_embeddings: List of tuples (post, embedding) for public posts.
        :return: Sorted list of posts by highest similarity.
        """
        recommendations = []
        for post, public_embedding in public_embeddings:
            if public_embedding is not None:
                max_similarity = max(
                    cosine_similarity([public_embedding], [fav_emb])[0][0]
                    for fav_emb in favorite_embeddings
                )
                recommendations.append({"post": post, "similarity": max_similarity})
        
        # Sort recommendations by similarity and extract only posts
        sorted_posts = [rec["post"] for rec in sorted(recommendations, key=lambda x: x["similarity"], reverse=True)]
        return sorted_posts
