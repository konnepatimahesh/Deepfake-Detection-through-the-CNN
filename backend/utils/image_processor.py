import cv2
import numpy as np
from PIL import Image
import os

class ImageProcessor:
    """
    Handles image preprocessing for deepfake detection
    """
    
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
    
    def load_image(self, image_path):
        """Load image from file path"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image from {image_path}")
            return img
        except Exception as e:
            raise Exception(f"Error loading image: {str(e)}")
    
    def preprocess_image(self, image_path):
        """
        Preprocess image for CNN model
        Returns: Normalized numpy array
        """
        try:
            # Load image
            img = self.load_image(image_path)
            
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize to target size
            img = cv2.resize(img, self.target_size)
            
            # Normalize pixel values to [0, 1]
            img = img.astype(np.float32) / 255.0
            
            # Add batch dimension
            img = np.expand_dims(img, axis=0)
            
            return img
            
        except Exception as e:
            raise Exception(f"Error preprocessing image: {str(e)}")
    
    def extract_faces(self, image_path):
        """
        Extract faces from image using Haar Cascade
        Returns: List of face images
        """
        try:
            img = self.load_image(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Load Haar Cascade for face detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            face_images = []
            for (x, y, w, h) in faces:
                face = img[y:y+h, x:x+w]
                face = cv2.resize(face, self.target_size)
                face_images.append(face)
            
            return face_images
            
        except Exception as e:
            raise Exception(f"Error extracting faces: {str(e)}")
    
    def analyze_image_quality(self, image_path):
        """
        Analyze image quality metrics
        Returns: Dictionary with quality metrics
        """
        try:
            img = self.load_image(image_path)
            
            # Calculate blur (Laplacian variance)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate brightness
            brightness = np.mean(gray)
            
            # Get image dimensions
            height, width = img.shape[:2]
            
            return {
                'blur_score': float(blur_score),  # Convert to Python float
                'brightness': float(brightness),  # Convert to Python float
                'width': int(width),              # Convert to Python int
                'height': int(height),            # Convert to Python int
                'is_blurry': bool(blur_score < 100)  # Convert to Python bool
            }
            
        except Exception as e:
            raise Exception(f"Error analyzing image quality: {str(e)}")
    
    def save_processed_image(self, image_array, output_path):
        """Save processed image to file"""
        try:
            # Remove batch dimension if present
            if len(image_array.shape) == 4:
                image_array = image_array[0]
            
            # Denormalize if needed
            if image_array.max() <= 1.0:
                image_array = (image_array * 255).astype(np.uint8)
            
            # Convert RGB to BGR for OpenCV
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            
            cv2.imwrite(output_path, image_array)
            
        except Exception as e:
            raise Exception(f"Error saving image: {str(e)}")