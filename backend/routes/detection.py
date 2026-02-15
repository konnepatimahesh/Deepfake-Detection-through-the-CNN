from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import db, User, SearchHistory
from models.cnn_model import DeepfakeDetector
from utils.image_processor import ImageProcessor
from utils.video_processor import VideoProcessor
from utils.file_utils import allowed_file, get_file_type, save_upload_file, delete_file, get_file_size
import os
from datetime import datetime

detection_bp = Blueprint('detection', __name__)

# Initialize processors and model
image_processor = ImageProcessor()
video_processor = VideoProcessor()
detector = DeepfakeDetector()
detector.load_model()


@detection_bp.route('/analyze/image', methods=['POST'])
@jwt_required()
def analyze_image():
    """
    Analyze uploaded image for deepfake detection
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename, 'image'):
            return jsonify({'error': 'Invalid file type. Only images are allowed.'}), 400
        
        # Save uploaded file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path, filename = save_upload_file(file, upload_folder)
        
        try:
            # Get file size
            file_size = get_file_size(file_path)
            
            # Analyze image quality
            quality_metrics = image_processor.analyze_image_quality(file_path)
            
            # Preprocess image
            processed_image = image_processor.preprocess_image(file_path)
            
            # Detect deepfake
            prediction, confidence = detector.predict_image(processed_image)
            
            # Extract faces (optional - for additional analysis)
            faces = image_processor.extract_faces(file_path)
            face_count = len(faces)
            
            # Save to search history
            search_record = SearchHistory(
                user_id=current_user_id,
                file_name=filename,
                file_type='image',
                detection_result=prediction,
                confidence_score=confidence,
                file_path=file_path
            )
            db.session.add(search_record)
            db.session.commit()
            
            # Prepare response
            response_data = {
                'success': True,
                'file_name': filename,
                'file_size_mb': file_size,
                'file_type': 'image',
                'prediction': prediction,
                'confidence': round(confidence * 100, 2),
                'face_count': face_count,
                'quality_metrics': quality_metrics,
                'timestamp': datetime.utcnow().isoformat(),
                'analysis_id': search_record.id
            }
            
            return jsonify(response_data), 200
            
        except Exception as e:
            # Delete uploaded file on error
            delete_file(file_path)
            raise e
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@detection_bp.route('/analyze/video', methods=['POST'])
@jwt_required()
def analyze_video():
    """
    Analyze uploaded video for deepfake detection
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        if not allowed_file(file.filename, 'video'):
            return jsonify({'error': 'Invalid file type. Only videos are allowed.'}), 400
        
        # Save uploaded file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path, filename = save_upload_file(file, upload_folder)
        
        try:
            # Get file size
            file_size = get_file_size(file_path)
            
            # Get video information
            video_info = video_processor.get_video_info(file_path)
            
            # Extract frames
            frames = video_processor.extract_frames(file_path, max_frames=30)
            
            # Preprocess frames
            processed_frames = video_processor.preprocess_frames(frames)
            
            # Detect deepfake
            prediction, confidence = detector.predict_video(processed_frames)
            
            # Analyze individual frames (optional)
            frame_analysis = detector.analyze_frames(processed_frames)
            
            # Analyze video quality
            quality_metrics = video_processor.analyze_video_quality(file_path)
            
            # Save to search history
            search_record = SearchHistory(
                user_id=current_user_id,
                file_name=filename,
                file_type='video',
                detection_result=prediction,
                confidence_score=confidence,
                file_path=file_path
            )
            db.session.add(search_record)
            db.session.commit()
            
            # Prepare response
            response_data = {
                'success': True,
                'file_name': filename,
                'file_size_mb': file_size,
                'file_type': 'video',
                'prediction': prediction,
                'confidence': round(confidence * 100, 2),
                'video_info': video_info,
                'frames_analyzed': len(frames),
                'frame_analysis': frame_analysis,
                'quality_metrics': quality_metrics,
                'timestamp': datetime.utcnow().isoformat(),
                'analysis_id': search_record.id
            }
            
            return jsonify(response_data), 200
            
        except Exception as e:
            # Delete uploaded file on error
            delete_file(file_path)
            raise e
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@detection_bp.route('/history', methods=['GET'])
@jwt_required()
def get_user_history():
    """
    Get analysis history for current user
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        # Query user's search history
        history_query = SearchHistory.query.filter_by(user_id=current_user_id)\
            .order_by(SearchHistory.timestamp.desc())
        
        # Paginate results
        pagination = history_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        history_items = [item.to_dict() for item in pagination.items]
        
        return jsonify({
            'success': True,
            'history': history_items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch history: {str(e)}'}), 500


@detection_bp.route('/history/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis_details(analysis_id):
    """
    Get detailed information about a specific analysis
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get analysis record
        analysis = SearchHistory.query.filter_by(
            id=analysis_id,
            user_id=current_user_id
        ).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify({
            'success': True,
            'analysis': analysis.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch analysis: {str(e)}'}), 500


@detection_bp.route('/history/<int:analysis_id>', methods=['DELETE'])
@jwt_required()
def delete_analysis(analysis_id):
    """
    Delete a specific analysis record
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get analysis record
        analysis = SearchHistory.query.filter_by(
            id=analysis_id,
            user_id=current_user_id
        ).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Delete associated file
        if analysis.file_path:
            delete_file(analysis.file_path)
        
        # Delete database record
        db.session.delete(analysis)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Analysis deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete analysis: {str(e)}'}), 500


@detection_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """
    Get statistics for current user
    """
    try:
        current_user_id = get_jwt_identity()
        
        # Get all user's analyses
        analyses = SearchHistory.query.filter_by(user_id=current_user_id).all()
        
        total_analyses = len(analyses)
        fake_count = sum(1 for a in analyses if a.detection_result == 'fake')
        real_count = sum(1 for a in analyses if a.detection_result == 'real')
        
        image_count = sum(1 for a in analyses if a.file_type == 'image')
        video_count = sum(1 for a in analyses if a.file_type == 'video')
        
        avg_confidence = sum(a.confidence_score for a in analyses) / total_analyses if total_analyses > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_analyses': total_analyses,
                'fake_detected': fake_count,
                'real_detected': real_count,
                'images_analyzed': image_count,
                'videos_analyzed': video_count,
                'average_confidence': round(avg_confidence * 100, 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch stats: {str(e)}'}), 500