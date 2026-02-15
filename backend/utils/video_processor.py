import cv2
import numpy as np
import os
from datetime import timedelta

class VideoProcessor:
    """
    Handles video preprocessing for deepfake detection
    """
    
    def __init__(self, target_size=(224, 224), frames_to_extract=30):
        self.target_size = target_size
        self.frames_to_extract = frames_to_extract
    
    def get_video_info(self, video_path):
        """
        Get video metadata
        Returns: Dictionary with video information
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'fps': float(fps),
                'frame_count': int(frame_count),
                'width': int(width),
                'height': int(height),
                'duration': float(duration),
                'duration_formatted': str(timedelta(seconds=int(duration)))
            }
            
        except Exception as e:
            raise Exception(f"Error getting video info: {str(e)}")
    
    def extract_frames(self, video_path, max_frames=None):
        """
        Extract frames from video uniformly
        Returns: List of frame arrays
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Determine number of frames to extract
            num_frames = max_frames or self.frames_to_extract
            num_frames = min(num_frames, frame_count)
            
            # Calculate frame indices to extract uniformly
            if num_frames >= frame_count:
                frame_indices = list(range(frame_count))
            else:
                frame_indices = np.linspace(0, frame_count - 1, num_frames, dtype=int)
            
            frames = []
            current_frame = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                if current_frame in frame_indices:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Resize frame
                    frame_resized = cv2.resize(frame_rgb, self.target_size)
                    
                    frames.append(frame_resized)
                
                current_frame += 1
                
                if len(frames) >= num_frames:
                    break
            
            cap.release()
            
            return frames
            
        except Exception as e:
            raise Exception(f"Error extracting frames: {str(e)}")
    
    def preprocess_frames(self, frames):
        """
        Preprocess extracted frames for CNN model
        Returns: Normalized numpy array
        """
        try:
            # Convert list to numpy array
            frames_array = np.array(frames, dtype=np.float32)
            
            # Normalize pixel values to [0, 1]
            frames_array = frames_array / 255.0
            
            return frames_array
            
        except Exception as e:
            raise Exception(f"Error preprocessing frames: {str(e)}")
    
    def extract_faces_from_video(self, video_path, max_frames=10):
        """
        Extract faces from video frames
        Returns: List of face images
        """
        try:
            # Extract frames
            frames = self.extract_frames(video_path, max_frames)
            
            # Load Haar Cascade
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            face_images = []
            
            for frame in frames:
                # Convert RGB to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                
                # Detect faces
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                # Extract first face from each frame
                if len(faces) > 0:
                    (x, y, w, h) = faces[0]  # Take first face
                    face = frame[y:y+h, x:x+w]
                    face = cv2.resize(face, self.target_size)
                    face_images.append(face)
            
            return face_images
            
        except Exception as e:
            raise Exception(f"Error extracting faces from video: {str(e)}")
    
    def save_frames(self, frames, output_dir, prefix="frame"):
        """
        Save extracted frames to directory
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            saved_paths = []
            for i, frame in enumerate(frames):
                output_path = os.path.join(output_dir, f"{prefix}_{i:04d}.jpg")
                
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                cv2.imwrite(output_path, frame_bgr)
                saved_paths.append(output_path)
            
            return saved_paths
            
        except Exception as e:
            raise Exception(f"Error saving frames: {str(e)}")
    
    def analyze_video_quality(self, video_path):
        """
        Analyze video quality by sampling frames
        Returns: Dictionary with quality metrics
        """
        try:
            # Extract a few frames for analysis
            frames = self.extract_frames(video_path, max_frames=5)
            
            blur_scores = []
            brightness_scores = []
            
            for frame in frames:
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                
                # Calculate blur
                blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                blur_scores.append(blur_score)
                
                # Calculate brightness
                brightness = np.mean(gray)
                brightness_scores.append(brightness)
            
            avg_blur = float(np.mean(blur_scores))
            avg_brightness = float(np.mean(brightness_scores))
            
            return {
                'avg_blur_score': avg_blur,
                'avg_brightness': avg_brightness,
                'is_blurry': bool(avg_blur < 100),
                'frames_analyzed': int(len(frames))
            }
            
        except Exception as e:
            raise Exception(f"Error analyzing video quality: {str(e)}")