from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import requests
import torch


class EmbeddingModel:
    """Generates embeddings using OpenAI's CLIP model."""

    def __init__(self):
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    def generate_text_embedding(self, text: str):
        """
        Generate a CLIP embedding for text.
        :param text: The text to embed.
        :return: A numpy array of the embedding.
        """
        inputs = self.clip_processor(text=[text], return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            return self.clip_model.get_text_features(**inputs).squeeze(0).numpy()

    def generate_image_embedding(self, image_url: str):
        """
        Generate a CLIP embedding for an image.
        :param image_url: URL of the image.
        :return: A numpy array of the embedding.
        """
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        image = Image.open(response.raw).convert("RGB")
        inputs = self.clip_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            return self.clip_model.get_image_features(**inputs).squeeze(0).numpy()
            