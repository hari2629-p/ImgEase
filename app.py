from flask import Flask, render_template, request, send_from_directory, jsonify, flash
from PIL import Image, ImageFilter, ImageEnhance
from werkzeug.utils import secure_filename  
import os
import uuid
import mimetypes
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a random secret key

# Configuration
UPLOAD_FOLDER = "static/output"
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
DEFAULT_DPI = 96

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size_mb(file_path):
    """Get file size in MB"""
    return round(os.path.getsize(file_path) / (1024 * 1024), 2)

def convert_units_to_pixels(value, unit, dpi=DEFAULT_DPI):
    """Convert different units to pixels"""
    if unit == "px":
        return int(value)
    elif unit == "in":
        return int(value * dpi)
    elif unit == "cm":
        return int((value / 2.54) * dpi)
    else:
        return int(value)

def process_image(file, width, height, unit, format_type, quality):
    """
    Process the uploaded image with various enhancements
    """
    try:
        # Convert units to pixels
        width_px = convert_units_to_pixels(width, unit)
        height_px = convert_units_to_pixels(height, unit)

        # Validate dimensions
        if width_px <= 0 or height_px <= 0:
            raise ValueError("Width and height must be positive numbers")

        if width_px > 10000 or height_px > 10000:
            raise ValueError("Maximum dimension is 10000 pixels")

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"imgease_{timestamp}_{uuid.uuid4().hex[:8]}.{format_type.lower()}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Open and process image
        img = Image.open(file)
        original_format = img.format
        original_size = img.size

        logger.info(f"Processing image: {original_size} -> ({width_px}, {height_px})")

        # Handle transparency for PNG/GIF
        if format_type.upper() in ['JPEG', 'JPG'] and img.mode in ('RGBA', 'LA', 'P'):
            # Create white background for JPEG
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif format_type.upper() == 'PNG' and img.mode != 'RGBA':
            img = img.convert('RGBA')
        elif format_type.upper() == 'WEBP':
            # WebP supports both RGB and RGBA
            pass
        else:
            img = img.convert('RGB')

        # Resize with high-quality resampling
        img_resized = img.resize((width_px, height_px), Image.Resampling.LANCZOS)

        # Save with appropriate settings
        save_kwargs = {'format': format_type.upper()}

        if format_type.upper() in ['JPEG', 'JPG']:
            save_kwargs.update({
                'quality': quality,
                'optimize': True,
                'progressive': True
            })
        elif format_type.upper() == 'PNG':
            save_kwargs.update({
                'optimize': True,
                'compress_level': 6
            })
        elif format_type.upper() == 'WEBP':
            save_kwargs.update({
                'quality': quality,
                'method': 6,
                'lossless': False if quality < 100 else True
            })

        img_resized.save(filepath, **save_kwargs)

        # Get file info
        output_size_mb = get_file_size_mb(filepath)

        logger.info(f"Image saved: {filename} ({output_size_mb}MB)")

        return {
            'success': True,
            'filename': filename,
            'original_size': original_size,
            'new_size': (width_px, height_px),
            'file_size_mb': output_size_mb,
            'original_format': original_format
        }

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {'success': False, 'error': str(e)}

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Validate file upload
            if 'image' not in request.files:
                flash('No file selected', 'error')
                return render_template("index.html")

            file = request.files['image']
            if file.filename == '':
                flash('No file selected', 'error')
                return render_template("index.html")

            if not allowed_file(file.filename):
                flash('Invalid file type. Please upload an image file.', 'error')
                return render_template("index.html")

            # Get form data with validation
            try:
                width = float(request.form["width"])
                height = float(request.form["height"])
                unit = request.form["unit"]
                format_type = request.form["format"]
                quality = int(request.form["quality"])
            except (ValueError, KeyError) as e:
                flash('Invalid form data. Please check your inputs.', 'error')
                return render_template("index.html")

            # Validate inputs
            if width <= 0 or height <= 0:
                flash('Width and height must be positive numbers', 'error')
                return render_template("index.html")

            if quality < 1 or quality > 100:
                flash('Quality must be between 1 and 100', 'error')
                return render_template("index.html")

            # Process the image
            result = process_image(file, width, height, unit, format_type, quality)

            if result['success']:
                flash('Image processed successfully!', 'success')
                return render_template("index.html",
                                     download_link=result['filename'],
                                     image_info=result)
            else:
                flash(f'Error processing image: {result["error"]}', 'error')
                return render_template("index.html")

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'error')
            return render_template("index.html")

    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    """Download processed image"""
    try:
        # Security check - ensure filename is safe
        if not filename or '..' in filename or '/' in filename:
            flash('Invalid filename', 'error')
            return render_template("index.html")

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(filepath):
            flash('File not found', 'error')
            return render_template("index.html")

        # Set proper MIME type
        mimetype = mimetypes.guess_type(filepath)[0]

        return send_from_directory(UPLOAD_FOLDER, filename,
                                 as_attachment=True,
                                 mimetype=mimetype)
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        flash('Error downloading file', 'error')
        return render_template("index.html")

@app.route("/api/image-info", methods=["POST"])
def get_image_info():
    """API endpoint to get image information without processing"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['image']
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        img = Image.open(file)
        return jsonify({
            'width': img.width,
            'height': img.height,
            'format': img.format,
            'mode': img.mode,
            'size_mb': round(len(file.read()) / (1024 * 1024), 2)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/cleanup")
def cleanup_old_files():
    """Clean up old processed images (optional maintenance endpoint)"""
    try:
        import time
        current_time = time.time()
        deleted_count = 0

        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                # Delete files older than 24 hours
                if current_time - os.path.getctime(filepath) > 24 * 3600:
                    os.remove(filepath)
                    deleted_count += 1

        return jsonify({
            'message': f'Cleaned up {deleted_count} old files',
            'deleted_count': deleted_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16MB.', 'error')
    return render_template("index.html"), 413

@app.errorhandler(500)
def internal_error(e):
    flash('An internal error occurred. Please try again.', 'error')
    return render_template("index.html"), 500

if __name__ == "__main__":
    # Set max file size
    app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
    app.run(debug=True, host='0.0.0.0', port=5000)
