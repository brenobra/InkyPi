from plugins.base_plugin.base_plugin import BasePlugin
from PIL import Image
from io import BytesIO
import requests
import logging
import json

logger = logging.getLogger(__name__)

# Cloudflare Workers AI text-to-image models
IMAGE_MODELS = [
    {
        "id": "@cf/black-forest-labs/flux-1-schnell",
        "name": "FLUX.1 Schnell (Recommended)",
        "description": "Fast, high-quality generation"
    },
    {
        "id": "@cf/bytedance/stable-diffusion-xl-lightning", 
        "name": "SDXL Lightning",
        "description": "Ultra-fast, 1024px images"
    },
    {
        "id": "@cf/lykon/dreamshaper-8-lcm",
        "name": "DreamShaper 8 LCM", 
        "description": "Photorealistic focus"
    },
    {
        "id": "@cf/stability/stable-diffusion-xl-base-1.0",
        "name": "Stable Diffusion XL Base",
        "description": "Reliable, versatile"
    },
    {
        "id": "@cf/runwayml/stable-diffusion-v1-5-img2img",
        "name": "Stable Diffusion 1.5 img2img", 
        "description": "Classic model"
    },
    {
        "id": "@cf/runwayml/stable-diffusion-v1-5-inpainting",
        "name": "Stable Diffusion 1.5 Inpainting",
        "description": "Advanced editing"
    }
]

DEFAULT_IMAGE_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CLOUDFLARE_API_BASE = "https://gateway.ai.cloudflare.com/v1/d7d9eea07df9b1cd0c93141bd99239b6/inky-pi/workers-ai"
class AIImage(BasePlugin):
    def generate_settings_template(self):
        template_params = super().generate_settings_template()
        template_params['api_key'] = {
            "required": True,
            "service": "Cloudflare",
            "expected_key": "CLOUDFLARE_API_TOKEN"
        }
        template_params['image_models'] = IMAGE_MODELS
        return template_params

    def generate_image(self, settings, device_config):
        api_token = device_config.load_env_key("CLOUDFLARE_API_TOKEN")
        if not api_token:
            raise RuntimeError("Cloudflare API Token not configured.")

        text_prompt = settings.get("textPrompt", "")
        if not text_prompt.strip():
            raise RuntimeError("Text prompt is required.")

        # Validate and get model
        image_model = settings.get('imageModel', DEFAULT_IMAGE_MODEL)
        valid_model_ids = [model['id'] for model in IMAGE_MODELS]
        if image_model not in valid_model_ids:
            image_model = DEFAULT_IMAGE_MODEL

        # Add e-ink optimization to prompt
        optimized_prompt = AIImage.optimize_prompt_for_eink(text_prompt)

        try:
            image = AIImage.generate_cloudflare_image(
                api_token,
                optimized_prompt,
                model=image_model
            )
            
            # Optimize image for e-ink display
            image = AIImage.optimize_image_for_eink(image, device_config.get_resolution())
            
        except Exception as e:
            logger.error(f"Failed to generate image with Cloudflare AI: {str(e)}")
            raise RuntimeError(f"Cloudflare AI request failed: {str(e)}")
        
        return image

    @staticmethod
    def generate_cloudflare_image(api_token, prompt, model=DEFAULT_IMAGE_MODEL):
        """Generate image using Cloudflare Workers AI"""
        logger.info(f"Generating image with model: {model}")
        logger.info(f"Prompt: {prompt}")
        
        url = f"{CLOUDFLARE_API_BASE}/run/{model}"
        
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            error_msg = f"Cloudflare AI API error: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    if 'errors' in error_data:
                        error_msg += f" - {error_data['errors'][0].get('message', 'Unknown error')}"
                except:
                    error_msg += f" - {response.text[:200]}"
            raise RuntimeError(error_msg)
        
        # The response should contain the image data
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        
        return image
    
    @staticmethod
    def optimize_prompt_for_eink(prompt):
        """Optimize prompt for e-ink display characteristics"""
        eink_optimizations = (
            " High contrast black and white, simple bold shapes, "
            "clean lines, minimal detail, strong contrast, "
            "suitable for monochrome display"
        )
        
        # Add e-ink optimizations if not already present
        if "black and white" not in prompt.lower() and "monochrome" not in prompt.lower():
            prompt += eink_optimizations
        
        return prompt
    
    @staticmethod
    def optimize_image_for_eink(image, target_resolution=(250, 122)):
        """Optimize generated image for e-ink display"""
        # Convert to grayscale first
        if image.mode != 'L':
            image = image.convert('L')
        
        # Resize maintaining aspect ratio
        image.thumbnail(target_resolution, Image.Resampling.LANCZOS)
        
        # Create new image with exact target size and paste centered
        final_image = Image.new('L', target_resolution, 255)  # White background
        
        # Calculate position to center the image
        x = (target_resolution[0] - image.size[0]) // 2
        y = (target_resolution[1] - image.size[1]) // 2
        
        final_image.paste(image, (x, y))
        
        # Increase contrast for better e-ink display
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(final_image)
        final_image = enhancer.enhance(1.5)  # Increase contrast by 50%
        
        # Convert back to RGB for compatibility with display system
        final_image = final_image.convert('RGB')
        
        return final_image
