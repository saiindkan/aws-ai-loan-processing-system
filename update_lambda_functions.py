#!/usr/bin/env python3
"""
Script to update Lambda functions with fixed code
"""

import boto3
import zipfile
import os
import tempfile
from pathlib import Path

def update_lambda_function(function_name, source_dir):
    """Update a Lambda function with new code"""
    try:
        # Initialize Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        print(f"📦 Updating {function_name}...")
        
        # Create a temporary zip file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            temp_zip_path = temp_zip.name
        
        # Create zip file with the function code
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
        
        # Read the zip file
        with open(temp_zip_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Update the Lambda function
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=zip_content
        )
        
        print(f"✅ Successfully updated {function_name}")
        print(f"   Version: {response['Version']}")
        print(f"   Last Modified: {response['LastModified']}")
        
        # Clean up
        os.unlink(temp_zip_path)
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating {function_name}: {str(e)}")
        return False

def main():
    """Update all Lambda functions"""
    print("🚀 Updating Lambda Functions")
    print("=" * 50)
    
    # Update risk assessment agent
    risk_agent_dir = "backend/lambda_functions/risk_agent"
    if os.path.exists(risk_agent_dir):
        success = update_lambda_function("risk-assessment-agent", risk_agent_dir)
        if not success:
            return
    
    # Update decision making agent
    decision_agent_dir = "backend/lambda_functions/decision_agent"
    if os.path.exists(decision_agent_dir):
        success = update_lambda_function("decision-making-agent", decision_agent_dir)
        if not success:
            return
    
    print("\n✅ All Lambda functions updated successfully!")
    print("💡 You can now run the complete workflow again")

if __name__ == "__main__":
    main()
