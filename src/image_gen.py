"""
Image generation module using MiniMax API.
Falls back to DALL-E if MiniMax is unavailable.
Includes prompt moderation for safety.
"""
import os
from typing import Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

# Blocked terms for image generation
BLOCKED_IMAGE_TERMS = [
    "nude", "naked", "sex", "porn", "gore", "blood", "violence",
    "kill", "murder", "torture", "abuse", "weapon", "gun", "knife",
    "hitler", "nazi", "killing", "death", "suicide", "self-harm",
]


class MiniMaxImageClient:
    """Client for MiniMax Image Generation API."""

    BASE_URL = "https://api.minimax.io"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.group_id = os.getenv("MINIMAX_GROUP_ID")

        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY not found in environment")

    def check_image_prompt(self, prompt: str) -> tuple[bool, str]:
        """
        Check if prompt is safe for image generation.
        Returns (is_safe, error_message).
        """
        prompt_lower = prompt.lower()

        for term in BLOCKED_IMAGE_TERMS:
            if term in prompt_lower:
                return False, f"Image prompt contains blocked content: '{term}'"

        if len(prompt) > 500:
            return False, "Image prompt is too long (max 500 characters)"

        return True, ""

    def generate_image(self, prompt: str, model: str = "image-01") -> dict:
        # Check prompt safety first
        is_safe, error_msg = self.check_image_prompt(prompt)
        if not is_safe:
            return {"error": error_msg, "image_url": None, "blocked": True}

        url = f"{self.BASE_URL}/v1/image_generation"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "prompt": prompt,
            "aspect_ratio": "16:9",
            "response_format": "url",
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                # MiniMax response: {"data": {"image_urls": ["..."]}}
                image_data = data.get("data", {})
                image_urls = image_data.get("image_urls", [])

                if image_urls and len(image_urls) > 0:
                    return {
                        "image_url": image_urls[0],
                        "prompt": prompt,
                        "model": model
                    }

                return {"error": "No image URL in response", "image_url": None}

        except httpx.HTTPStatusError as e:
            print(f"MiniMax Image API HTTP error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP {e.response.status_code}", "image_url": None}

        except Exception as e:
            print(f"MiniMax Image API error: {e}")
            return {"error": str(e), "image_url": None}


def generate_christian_image(prompt: str) -> dict:
    """
    Generate a Christian-themed image using MiniMax API.
    Falls back to DALL-E if MiniMax fails.
    """
    # Check prompt safety first (before adding Christian prefix)
    client_check = MiniMaxImageClient()
    is_safe, error_msg = client_check.check_image_prompt(prompt)
    if not is_safe:
        return {"error": error_msg, "image_url": None, "blocked": True}

    # Sanitize prompt for Christian content
    safe_prompt = f"Christian religious art, {prompt}, reverent, peaceful, respectful, sacred, biblical"

    # Try MiniMax first
    try:
        client = MiniMaxImageClient()
        result = client.generate_image(safe_prompt)
        if result.get("image_url"):
            return result
    except Exception as e:
        print(f"MiniMax image generation failed: {e}")

    # Fallback to DALL-E
    return _generate_dalle_image(prompt)


def _generate_dalle_image(prompt: str) -> dict:
    """Fallback image generation using DALL-E."""
    from openai import OpenAI

    safe_prompt = f"Christian religious art, {prompt}, reverent, peaceful, respectful"

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.images.generate(
            model="dall-e-3",
            prompt=safe_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        return {
            "image_url": response.data[0].url,
            "prompt": prompt,
            "revised_prompt": response.data[0].revised_prompt if hasattr(response.data[0], 'revised_prompt') else None,
            "fallback": True
        }

    except Exception as e:
        print(f"DALL-E image generation error: {e}")
        return {
            "error": str(e),
            "image_url": None
        }


def get_minimax_image_client() -> MiniMaxImageClient:
    """Get or create MiniMax image client."""
    return MiniMaxImageClient()