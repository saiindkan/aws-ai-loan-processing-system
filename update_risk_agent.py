#!/usr/bin/env python3
"""
Script to update the risk assessment agent Lambda function
"""

import boto3

def update_risk_agent():
    """Update the risk assessment agent Lambda function"""
    try:
        # Initialize Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        print("📦 Updating risk-assessment-agent...")
        
        # Read the zip file
        with open('backend/lambda_functions/risk_agent/risk_agent.zip', 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Update the Lambda function
        response = lambda_client.update_function_code(
            FunctionName='risk-assessment-agent',
            ZipFile=zip_content
        )
        
        print(f"✅ Successfully updated risk-assessment-agent")
        print(f"   Version: {response['Version']}")
        print(f"   Last Modified: {response['LastModified']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating risk-assessment-agent: {str(e)}")
        return False

if __name__ == "__main__":
    update_risk_agent()
