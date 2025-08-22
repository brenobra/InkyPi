from flask import Blueprint, request, jsonify, current_app, render_template, send_file, make_response
import os

main_bp = Blueprint("main", __name__)

@main_bp.route('/')
def main_page():
    device_config = current_app.config['DEVICE_CONFIG']
    return render_template('inky.html', 
                         config=device_config.get_config(), 
                         plugins=device_config.get_plugins())

@main_bp.route('/current-image')
def current_image():
    """Serve the current image with proper cache headers to prevent caching"""
    device_config = current_app.config['DEVICE_CONFIG']
    current_image_path = device_config.current_image_file
    
    if not os.path.exists(current_image_path):
        # Return 404 if image doesn't exist
        return "Image not found", 404
    
    # Create response with the image file
    response = make_response(send_file(current_image_path, mimetype='image/png'))
    
    # Set cache headers to prevent browser caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response