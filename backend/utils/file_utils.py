import os
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename, file_type='image'):
    """
    Check if file extension is allowed
    file_type: 'image' or 'video'
    """
    if not filename:
        return False
    
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'image':
        return ext in Config.ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'video':
        return ext in Config.ALLOWED_VIDEO_EXTENSIONS
    else:
        # Allow both
        return ext in (Config.ALLOWED_IMAGE_EXTENSIONS | Config.ALLOWED_VIDEO_EXTENSIONS)

def get_file_type(filename):
    """
    Determine if file is image or video
    Returns: 'image', 'video', or None
    """
    if not filename or '.' not in filename:
        return None
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if ext in Config.ALLOWED_IMAGE_EXTENSIONS:
        return 'image'
    elif ext in Config.ALLOWED_VIDEO_EXTENSIONS:
        return 'video'
    else:
        return None

def save_upload_file(file, upload_folder):
    """
    Save uploaded file securely
    Returns: (saved_path, filename)
    """
    try:
        # Create upload folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)
        
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Generate unique filename if file already exists
        base_name, ext = os.path.splitext(filename)
        counter = 1
        final_filename = filename
        
        while os.path.exists(os.path.join(upload_folder, final_filename)):
            final_filename = f"{base_name}_{counter}{ext}"
            counter += 1
        
        # Save file
        file_path = os.path.join(upload_folder, final_filename)
        file.save(file_path)
        
        return file_path, final_filename
        
    except Exception as e:
        raise Exception(f"Error saving file: {str(e)}")

def delete_file(file_path):
    """Delete file if it exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        return False

def get_file_size(file_path):
    """Get file size in MB"""
    try:
        if os.path.exists(file_path):
            size_bytes = os.path.getsize(file_path)
            size_mb = size_bytes / (1024 * 1024)
            return round(size_mb, 2)
        return 0
    except Exception as e:
        print(f"Error getting file size: {str(e)}")
        return 0