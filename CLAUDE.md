# InkyPi Project - Claude Code Documentation

## Project Overview
InkyPi is a Flask-based web application that manages e-ink displays (Pimoroni Inky, Waveshare) with a plugin-based architecture for displaying various content types.

## Key Architecture Components

### Main Application
- **Entry Point**: `src/inkypi.py` - Flask app with Waitress WSGI server on port 80
- **Dependencies**: Config, DisplayManager, RefreshTask stored in app.config
- **Background Task**: Continuous refresh loop for display updates

### Plugin System
- **Base Class**: `src/plugins/base_plugin/base_plugin.py` - BasePlugin class
- **Registry**: `src/plugins/plugin_registry.py` - Dynamic plugin loading
- **Plugin Structure**:
  - `plugin-info.json` - metadata (display_name, id, class)
  - `{plugin_id}.py` - main plugin class  
  - `settings.html` - configuration UI
  - `render/` - HTML/CSS templates (optional)
  - `icon.png` - UI icon

### Data Models
- **Config**: `src/config.py` - JSON-based device configuration
- **Models**: `src/model.py` - PlaylistManager, Playlist, PluginInstance, RefreshInfo
- **Display**: `src/display/display_manager.py` - Display abstraction layer
- **Refresh**: `src/refresh_task.py` - Background threading and scheduling

### Web Interface Blueprints
- `src/blueprints/main.py` - Core UI and playlist management
- `src/blueprints/settings.py` - Device configuration  
- `src/blueprints/plugin.py` - Plugin management
- `src/blueprints/playlist.py` - Playlist CRUD operations

## Plugin Development Interface
```python
class YourPlugin(BasePlugin):
    def generate_image(self, settings, device_config):
        # Return PIL Image
        pass
    
    def generate_settings_template(self):
        # Return template parameters for UI
        pass
```

## Configuration Files
- **Device Config**: `src/config/device.json` (auto-created)
- **Logging**: `src/config/logging.conf`
- **Requirements**: `install/requirements.txt`, `install/requirements-dev.txt`

## Supported Display Types
- Pimoroni Inky displays
- Waveshare e-Paper displays (epd* pattern matching)

## Key Features
- Time-based playlist scheduling
- Plugin instance management with individual refresh settings
- Image hash comparison for smart display updates
- HTML template rendering with screenshot conversion
- Direct PIL image generation
- Web-based configuration interface

## Development Commands
- **Install**: `install/install.sh`
- **Update**: `install/update.sh`  
- **Uninstall**: `install/uninstall.sh`
- **Test Plugin**: `scripts/test_plugin.py`

## AI Image Plugin - Cloudflare Integration ✅ IMPLEMENTED
- **Status**: Fully implemented, tested, and enhanced with color support
- **API Endpoint**: `https://gateway.ai.cloudflare.com/v1/d7d9eea07df9b1cd0c93141bd99239b6/inky-pi/workers-ai`
- **Authentication**: Bearer token via `CLOUDFLARE_API_TOKEN` environment variable
- **Available Models**:
  - @cf/black-forest-labs/flux-1-schnell (default, recommended)
  - @cf/bytedance/stable-diffusion-xl-lightning
  - @cf/lykon/dreamshaper-8-lcm
  - @cf/stability/stable-diffusion-xl-base-1.0
  - @cf/runwayml/stable-diffusion-v1-5-img2img
  - @cf/runwayml/stable-diffusion-v1-5-inpainting
- **Style Options**: 
  - 10 selectable prompt enhancement styles (None, E-ink Optimized, High Contrast, Minimalist, Sketch, Vintage Poster, Silhouette, Technical Diagram, Comic Book, Woodcut Print)
  - User-configurable dropdown with dynamic descriptions
  - Color-neutral style prompts for both color and grayscale modes
  - Default: "None" for no style enhancement
- **Color Support**: 
  - **NEW**: "Convert to Grayscale" checkbox for user control
  - Default: Color preservation for color displays (Inky Spectra, etc.)
  - Optional: Grayscale conversion for B&W displays or aesthetic preference
  - Automatic mode detection and optimization
- **E-ink Optimizations**: 
  - Dynamic image resizing based on device configuration
  - Image centering for any display resolution
  - Contrast enhancement for better e-ink visibility
  - Color/grayscale aware background creation
- **Testing**: Core functionality and color support tested and verified
- **Deployment**: Running on Pi Zero 2W at 192.168.0.153

## Implementation Status
- ✅ Enhanced AI Image plugin with Cloudflare Workers AI
- ✅ Replaced OpenAI DALL-E with superior models (FLUX.1, SDXL, etc.)
- ✅ E-ink display optimizations implemented
- ✅ Web interface updated with model selection
- ✅ **Style dropdown with 10 prompt enhancement options**
- ✅ **UI field order: Prompt → Style → Model → Grayscale Option**
- ✅ **Dynamic resolution support - no more hardcoded 250x122**
- ✅ **Color display support with user-controlled grayscale conversion**
- ✅ **Color-neutral style prompts for versatile usage**
- ✅ Code tested and committed to GitHub
- ✅ **Fixed Cloudflare API response parsing (base64 JSON handling)**
- ✅ **Fully tested and verified working on Pi at 192.168.0.153**
- ✅ **Production ready with full color support**

## AI Image Plugin Status - COMPLETE ✅
- **API Integration**: Cloudflare Workers AI fully functional
- **Models Available**: FLUX.1 Schnell, SDXL Lightning, DreamShaper 8 LCM, SDXL Base, SD 1.5 variants
- **Style Options**: 10 selectable prompt enhancement styles with color-neutral prompts
- **Color Support**: Full color display support with optional grayscale conversion
- **Testing Results**: Successfully generates and displays color/grayscale images on e-ink screen
- **Error Resolution**: Fixed "cannot identify image file" issue with proper JSON/base64 parsing
- **Web Interface**: Fully functional with Prompt → Style → Model → Grayscale Option and real-time updates
- **Status**: Ready for production use with enhanced color capabilities

## Repository Information
- **Original**: https://github.com/fatihak/InkyPi
- **Fork**: https://github.com/brenobra/InkyPi
- **Remote Pi**: 192.168.0.153 (PiZero 2W running InkyPi)

## Important Notes
- Plugins are dynamically loaded at startup via importlib
- Display updates use background threading to avoid blocking web interface
- Image processing pipeline: orientation → resizing → enhancement → inversion
- Playlist priority determined by time range (shorter ranges = higher priority)
- Plugin instances can have interval-based or scheduled refresh settings

## Common Plugin Types
- **Clock**: Various clock faces with PIL drawing
- **Weather**: API integration with HTML template rendering
- **Calendar**: Event display with custom styling
- **Image Sources**: URL, folder, upload, Unsplash, APOD
- **AI Integration**: Text and image generation
- **Content Feeds**: Comics, newspapers, Wikipedia

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
Anything related to the project itself, we want to make sure you fully understand my request by asking questions and implementing changes only after it is fully understood. You may edit the .md file at any time without permission.