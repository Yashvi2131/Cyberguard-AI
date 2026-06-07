"""
CyberGuard AI X - AI Prediction Routes
Real-time prediction and explainability APIs
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'ml'))

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

ai_bp = Blueprint('ai', __name__)


def get_predictor_safe():
    try:
        from predict import get_predictor
        return get_predictor()
    except Exception as e:
        return None


@ai_bp.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    """Run full AI prediction on complaint text"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    text = data.get('text', '').strip()
    language = data.get('language', None)

    if not text or len(text) < 5:
        return jsonify({'error': 'Text too short for analysis (minimum 5 characters)'}), 400

    predictor = get_predictor_safe()
    if not predictor:
        return jsonify({
            'error': 'AI model not loaded. Please run: cd ml && python train_model.py',
            'code': 'MODEL_NOT_FOUND'
        }), 503

    if not predictor.pipeline:
        return jsonify({
            'error': 'Model pipeline not ready. Please run: cd ml && python train_model.py',
            'code': 'MODEL_NOT_READY'
        }), 503

    try:
        result = predictor.predict(text, language)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500


@ai_bp.route('/classify', methods=['POST'])
@jwt_required()
def classify_only():
    """Quick classification without full pipeline"""
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Text required'}), 400

    predictor = get_predictor_safe()
    if not predictor or not predictor.pipeline:
        return jsonify({'error': 'Model not available'}), 503

    processed = predictor.preprocessor.preprocess(text)
    category = predictor.pipeline.predict([processed])[0]
    probs = predictor.pipeline.predict_proba([processed])[0]
    confidence = float(max(probs) * 100)

    return jsonify({
        'category': category,
        'confidence': round(confidence, 2)
    })


@ai_bp.route('/severity', methods=['POST'])
@jwt_required()
def analyze_severity():
    """Analyze severity of complaint text"""
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Text required'}), 400

    predictor = get_predictor_safe()
    if not predictor:
        return jsonify({'error': 'Service not available'}), 503

    result = predictor.severity_analyzer.analyze(text)
    return jsonify(result)


@ai_bp.route('/department', methods=['POST'])
@jwt_required()
def recommend_department():
    """Recommend department for a category"""
    data = request.get_json()
    category = data.get('category', '')
    severity = data.get('severity', 'Low')

    predictor = get_predictor_safe()
    if not predictor:
        return jsonify({'error': 'Service not available'}), 503

    result = predictor.department_recommender.recommend(category, severity)
    return jsonify(result)


@ai_bp.route('/model-info', methods=['GET'])
@jwt_required()
def model_info():
    """Get information about the ML model"""
    return jsonify({
        'model': 'TF-IDF + Logistic Regression',
        'version': '1.0.0',
        'categories': [
            'Phishing', 'Hacking', 'Malware', 'Online Fraud',
            'Financial Fraud', 'Identity Theft', 'Cyberbullying'
        ],
        'languages_supported': ['English', 'Hindi', 'Gujarati'],
        'future_models': ['BERT', 'RoBERTa', 'DistilBERT', 'LLM-based Classification'],
        'features': ['TF-IDF Vectorization', 'Logistic Regression', 'Severity Analysis', 'Department Recommendation']
    })
