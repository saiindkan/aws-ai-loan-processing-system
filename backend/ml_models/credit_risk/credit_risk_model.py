"""
AWS SageMaker Credit Risk Prediction Model
This model predicts the probability of loan default based on applicant data
"""

import pandas as pd
import numpy as np
import boto3
import joblib
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import sagemaker
from sagemaker.sklearn import SKLearn
from sagemaker.sklearn.model import SKLearnModel
import os

class CreditRiskModel:
    def __init__(self):
        self.sagemaker_session = sagemaker.Session()
        self.role = os.environ.get('SAGEMAKER_ROLE', 'arn:aws:iam::YOUR_ACCOUNT:role/AILoanSageMakerExecutionRole')
        self.bucket = os.environ.get('S3_BUCKET', 'ai-loan-models-millionaire-20250923-01')
        self.model_name = 'credit-risk-model'
        
    def prepare_training_data(self):
        """Generate synthetic training data for demonstration"""
        np.random.seed(42)
        n_samples = 10000
        
        # Generate synthetic features
        data = {
            'credit_score': np.random.normal(650, 100, n_samples).astype(int),
            'annual_income': np.random.lognormal(10, 0.5, n_samples),
            'debt_to_income_ratio': np.random.beta(2, 5, n_samples) * 0.6,
            'employment_years': np.random.exponential(5, n_samples),
            'loan_amount': np.random.lognormal(9, 0.8, n_samples),
            'age': np.random.normal(35, 10, n_samples).astype(int),
            'loan_purpose_score': np.random.randint(1, 5, n_samples),
            'previous_defaults': np.random.poisson(0.3, n_samples),
            'savings_balance': np.random.lognormal(8, 1, n_samples)
        }
        
        # Calculate default probability based on features
        default_prob = (
            (data['credit_score'] < 600) * 0.3 +
            (data['debt_to_income_ratio'] > 0.4) * 0.2 +
            (data['employment_years'] < 2) * 0.15 +
            (data['previous_defaults'] > 0) * 0.25 +
            (data['loan_amount'] / data['annual_income'] > 0.5) * 0.1 +
            np.random.normal(0, 0.05, n_samples)
        )
        
        data['defaulted'] = (default_prob > 0.3).astype(int)
        
        return pd.DataFrame(data)
    
    def train_model(self, training_data_path=None):
        """Train the credit risk model using SageMaker"""
        try:
            # Prepare training data
            if training_data_path:
                df = pd.read_csv(training_data_path)
            else:
                df = self.prepare_training_data()
            
            # Feature engineering
            df['loan_to_income_ratio'] = df['loan_amount'] / df['annual_income']
            df['credit_score_normalized'] = (df['credit_score'] - 300) / 550
            
            # Select features
            feature_columns = [
                'credit_score_normalized', 'annual_income', 'debt_to_income_ratio',
                'employment_years', 'loan_amount', 'age', 'loan_purpose_score',
                'previous_defaults', 'loan_to_income_ratio'
            ]
            
            X = df[feature_columns]
            y = df['defaulted']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            
            print("Model Performance:")
            print(classification_report(y_test, y_pred))
            print(f"Accuracy: {model.score(X_test_scaled, y_test):.3f}")
            
            # Save model artifacts
            model_artifacts = {
                'model': model,
                'scaler': scaler,
                'feature_columns': feature_columns,
                'accuracy': model.score(X_test_scaled, y_test)
            }
            
            # Upload to S3 for SageMaker
            self._upload_model_to_s3(model_artifacts)
            
            return model_artifacts
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            raise e
    
    def _upload_model_to_s3(self, model_artifacts):
        """Upload trained model to S3"""
        s3_client = boto3.client('s3')
        
        # Save model locally first
        local_model_path = '/tmp/credit_risk_model.pkl'
        joblib.dump(model_artifacts, local_model_path)
        
        # Upload to S3
        s3_key = f'models/{self.model_name}/model.pkl'
        s3_client.upload_file(local_model_path, self.bucket, s3_key)
        
        print(f"Model uploaded to s3://{self.bucket}/{s3_key}")

# Training script for SageMaker
def train():
    """Training function for SageMaker"""
    model = CreditRiskModel()
    model.train_model()
    print("Model training completed successfully")

if __name__ == "__main__":
    train()
