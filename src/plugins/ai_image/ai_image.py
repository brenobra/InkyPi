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
        "description": "Fast, high-quality generation (square images)"
    },
    {
        "id": "@cf/bytedance/stable-diffusion-xl-lightning", 
        "name": "SDXL Lightning",
        "description": "Ultra-fast, supports display ratio"
    },
    {
        "id": "@cf/lykon/dreamshaper-8-lcm",
        "name": "DreamShaper 8 LCM", 
        "description": "Photorealistic focus, supports display ratio"
    },
    {
        "id": "@cf/stability/stable-diffusion-xl-base-1.0",
        "name": "Stable Diffusion XL Base",
        "description": "Reliable, versatile, supports display ratio"
    },
    {
        "id": "@cf/runwayml/stable-diffusion-v1-5-img2img",
        "name": "Stable Diffusion 1.5 img2img", 
        "description": "Classic model, supports display ratio"
    },
    {
        "id": "@cf/runwayml/stable-diffusion-v1-5-inpainting",
        "name": "Stable Diffusion 1.5 Inpainting",
        "description": "Advanced editing, supports display ratio"
    }
]

# Style options for prompt enhancement
STYLE_OPTIONS = [
    {
        "id": "none",
        "name": "None",
        "description": "No style enhancement",
        "prompt_append": ""
    },
    {
        "id": "eink_optimized",
        "name": "E-ink Optimized", 
        "description": "Optimized for e-ink displays",
        "prompt_append": " High contrast, simple bold shapes, clean lines, minimal detail, strong definition, suitable for electronic paper display"
    },
    {
        "id": "high_contrast",
        "name": "High Contrast",
        "description": "Bold shapes with strong definition",
        "prompt_append": " High contrast, bold shapes, strong definition"
    },
    {
        "id": "minimalist",
        "name": "Minimalist",
        "description": "Clean and simple design",
        "prompt_append": " Minimalist design, clean simple lines, uncluttered composition"
    },
    {
        "id": "sketch_style",
        "name": "Sketch Style",
        "description": "Hand-drawn appearance",
        "prompt_append": " Sketch style, line art, drawing style"
    },
    {
        "id": "vintage_poster",
        "name": "Vintage Poster",
        "description": "Classic poster design",
        "prompt_append": " Vintage poster style, bold typography, simple graphics"
    },
    {
        "id": "silhouette",
        "name": "Silhouette",
        "description": "Strong shapes and contrast",
        "prompt_append": " Strong silhouettes, solid shapes, dramatic contrast"
    },
    {
        "id": "technical_diagram",
        "name": "Technical Diagram",
        "description": "Clean technical illustration",
        "prompt_append": " Technical illustration, clean diagrams, blueprint style"
    },
    {
        "id": "comic_book",
        "name": "Comic Book",
        "description": "Comic art styling",
        "prompt_append": " Comic book art style, bold outlines, high contrast shading"
    },
    {
        "id": "woodcut_print",
        "name": "Woodcut Print",
        "description": "Traditional printmaking style",
        "prompt_append": " Woodcut print style, bold carved lines, traditional printmaking aesthetic"
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
        template_params['style_options'] = STYLE_OPTIONS
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

        # Apply selected style to prompt
        style_option = settings.get('styleOption', 'none')
        optimized_prompt = AIImage.apply_style_to_prompt(text_prompt, style_option)

        try:
            # Get display resolution for aspect ratio support
            display_resolution = device_config.get_resolution()
            
            image = AIImage.generate_cloudflare_image(
                api_token,
                optimized_prompt,
                model=image_model,
                width=display_resolution[0],
                height=display_resolution[1]
            )
            
            # Optimize image for e-ink display
            convert_to_grayscale = settings.get("convertToGrayscale", False)
            image = AIImage.optimize_image_for_eink(image, device_config.get_resolution(), convert_to_grayscale)
            
        except Exception as e:
            logger.error(f"Failed to generate image with Cloudflare AI: {str(e)}")
            raise RuntimeError(f"Cloudflare AI request failed: {str(e)}")
        
        return image

    @staticmethod
    def generate_cloudflare_image(api_token, prompt, model=DEFAULT_IMAGE_MODEL, width=None, height=None):
        """Generate image using Cloudflare Workers AI"""
        logger.info(f"Generating image with model: {model}")
        logger.info(f"Prompt: {prompt}")
        
        url = f"{CLOUDFLARE_API_BASE}/run/{model}"
        
        headers = {
            "Authorization": f"Bearer {api_token}",
            "cf-aig-authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
        # Build payload with prompt
        payload = {
            "prompt": prompt
        }
        
        # Add width/height for models that support it (all except FLUX.1 Schnell)
        if model != "@cf/black-forest-labs/flux-1-schnell" and width and height:
            payload["width"] = width
            payload["height"] = height
            logger.info(f"Using custom dimensions: {width}x{height}")
        else:
            logger.info("Using default dimensions (model doesn't support custom size)")
        
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
        
        # Parse the JSON response to get the base64 image data
        try:
            response_data = response.json()
            if 'result' in response_data and 'image' in response_data['result']:
                # Image is base64 encoded in the result.image field
                import base64
                image_b64 = response_data['result']['image']
                image_data = base64.b64decode(image_b64)
                image = Image.open(BytesIO(image_data))
            else:
                # Fallback: try direct binary response
                image_data = response.content
                image = Image.open(BytesIO(image_data))
        except (json.JSONDecodeError, KeyError):
            # If JSON parsing fails, try treating as direct image data
            image_data = response.content
            image = Image.open(BytesIO(image_data))
        
        return image
    
    @staticmethod
    def apply_style_to_prompt(prompt, style_id):
        """Apply selected style enhancement to prompt"""
        # Find the style option by id
        style_append = ""
        for style in STYLE_OPTIONS:
            if style['id'] == style_id:
                style_append = style['prompt_append']
                break
        
        # Apply style enhancement
        if style_append:
            prompt += style_append
        
        return prompt
    
    @staticmethod
    def optimize_image_for_eink(image, target_resolution, convert_to_grayscale=False):
        """Optimize generated image for e-ink display"""
        # Convert to grayscale if requested
        if convert_to_grayscale and image.mode != 'L':
            image = image.convert('L')
        
        # Resize maintaining aspect ratio
        image.thumbnail(target_resolution, Image.Resampling.LANCZOS)
        
        # Create new image with exact target size and paste centered
        if convert_to_grayscale:
            final_image = Image.new('L', target_resolution, 255)  # White background for grayscale
        else:
            final_image = Image.new('RGB', target_resolution, (255, 255, 255))  # White background for color
        
        # Calculate position to center the image
        x = (target_resolution[0] - image.size[0]) // 2
        y = (target_resolution[1] - image.size[1]) // 2
        
        final_image.paste(image, (x, y))
        
        # Increase contrast for better e-ink display
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(final_image)
        final_image = enhancer.enhance(1.5)  # Increase contrast by 50%
        
        # Convert to RGB for compatibility with display system (if not already)
        if final_image.mode != 'RGB':
            final_image = final_image.convert('RGB')
        
        return final_image
