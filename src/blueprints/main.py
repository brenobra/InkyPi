from flask import Blueprint, request, jsonify, current_app, render_template
import os
import time

main_bp = Blueprint("main", __name__)

@main_bp.route('/')
def main_page():
    device_config = current_app.config['DEVICE_CONFIG']
    
    # Get cache-busting parameter for current image
    current_image_path = device_config.current_image_file
    image_cache_bust = int(time.time())  # Default to current timestamp
    
    try:
        if os.path.exists(current_image_path):
            # Use file modification time as cache-busting parameter
            image_cache_bust = int(os.path.getmtime(current_image_path))
    except:
        pass  # Use default timestamp if file doesn't exist or error occurs
    
    return render_template('inky.html', 
                         config=device_config.get_config(), 
                         plugins=device_config.get_plugins(),
                         image_cache_bust=image_cache_bust)