def parse_mastodon_post(post):
    """
    Extract relevant fields from a Mastodon post.
    :param post: Mastodon post object.
    :return: Dictionary containing text, media URLs, and metadata.
    """
    # Extract text content
    text = post.get("content", "")
    # Extract image URLs from media attachments
    media_urls = [
        media["url"] for media in post.get("media_attachments", []) if media["type"] == "image"
    ]
    # Extract hashtags
    tags = [tag["name"] for tag in post.get("tags", [])]
    # Extract sensitive content flag
    sensitive = post.get("sensitive", False)

    return {
        "text": text,
        "media_urls": media_urls,
        "tags": tags,
        "sensitive": sensitive,
    }
    