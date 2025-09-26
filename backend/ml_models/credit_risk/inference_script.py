"""
SageMaker Inference Script for Credit Risk Model
This script handles model loading and prediction for the SageMaker endpoint
"""

import json
import joblib
import numpy as np
import os

def model_fn(model_dir):
    """Load the model from the model directory"""
    model_path = os.path.join(model_dir, 'model.pkl')
    model_artifacts = joblib.load(model_path)
    return model_artifacts

def input_fn(request_body, request_content_type):
    """Parse input data"""
    if request_content_type == 'application/json':
        input_data = json.loads(request_body)
        return input_data
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """Make prediction using the loaded model"""
    try:
        # Extract model components
        sklearn_model = model['model']
        scaler = model['scaler']
        feature_columns = model['feature_columns']
        
        # Prepare features in correct order
        features = []
        for col in feature_columns:
            features.append(input_data[col])
        
        # Convert to numpy array and reshape
        features_array = np.array(features).reshape(1, -1)
        
        # Scale features
        features_scaled = scaler.transform(features_array)
        
        # Make prediction
        risk_score = sklearn_model.predict_proba(features_scaled)[0][1]
        
        # Calculate confidence based on prediction probability
        confidence = abs(risk_score - 0.5) * 2  # Higher confidence for extreme predictions
        
        return {
            'risk_score': float(risk_score),
            'confidence': float(confidence),
            'prediction': int(risk_score > 0.5)
        }
        
    except Exception as e:
        return {
            'risk_score': 0.5,
            'confidence': 0.0,
            'prediction': 0,
            'error': str(e)
        }

def output_fn(prediction, content_type):
    """Format the prediction output"""
    if content_type == 'application/json':
        return json.dumps(prediction)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")
