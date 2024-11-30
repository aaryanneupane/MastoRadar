import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def combine_embeddings(text_embedding=None, image_embeddings=[]):
    """
    Combine text and image embeddings into a single vector.
    :param text_embedding: Text embedding vector.
    :param image_embeddings: List of image embedding vectors.
    :return: Combined embedding vector or None if no embeddings exist.
    """
    embeddings = []
    if text_embedding is not None:
        embeddings.append(text_embedding)
    embeddings.extend(image_embeddings)
    return np.mean(embeddings, axis=0) if embeddings else None


def compute_similarity(favorite_embeddings, public_embeddings):
    """
    Compute similarity scores between favorite embeddings and public embeddings.
    :param favorite_embeddings: List of embeddings for favorited posts.
    :param public_embeddings: List of tuples (post, embedding) for public posts.
    :return: List of dictionaries containing posts and their similarity scores.
    """
    similarities = []
    for post, public_embedding in public_embeddings:
        if public_embedding is not None:
            max_similarity = max(
                cosine_similarity([public_embedding], [fav_emb])[0][0]
                for fav_emb in favorite_embeddings
            )
            similarities.append({"post": post, "similarity": max_similarity})
    return sorted(similarities, key=lambda x: x["similarity"], reverse=True)
    