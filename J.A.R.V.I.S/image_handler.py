import os
import requests
import io
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

class ImageHandler:
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.stability_api_key = os.getenv("STABILITY_API_KEY")
        self.hf_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

    def generate_image(self, prompt, provider="Hugging Face", width=1024, height=1024):
        if provider == "Stability AI (Core)":
            return self._generate_stability(prompt, width, height)
        else:
            return self._generate_hf(prompt, width, height)

    def _generate_hf(self, prompt, width, height):
        if not self.hf_api_key:
            raise ValueError("HUGGINGFACE_API_KEY is not set. Please add it to your .env file.")
            
        headers = {"Authorization": f"Bearer {self.hf_api_key}"}
        payload = {"inputs": prompt}
        
        response = requests.post(self.hf_url, headers=headers, json=payload)
        
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        elif response.status_code == 503:
             raise Exception("Model is currently loading on Hugging Face. Please wait a few seconds and try again.")
        else:
            raise Exception(f"API Error ({response.status_code}): {response.text}")
            
    def _generate_stability(self, prompt, width, height):
        if not self.stability_api_key:
            raise ValueError("STABILITY_API_KEY is not set. Please add it to your .env file.")
            
        url = "https://api.stability.ai/v2beta/stable-image/generate/core"
        
        aspect_ratio = "1:1"
        if width > height:
            aspect_ratio = "16:9"
        elif height > width:
            aspect_ratio = "9:16"
            
        headers = {
            "Authorization": f"Bearer {self.stability_api_key}",
            "Accept": "image/*"
        }
        
        files = {
            "prompt": (None, prompt),
            "output_format": (None, "png"),
            "aspect_ratio": (None, aspect_ratio)
        }
        
        response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            raise Exception(f"Stability API Error ({response.status_code}): {response.text}")
