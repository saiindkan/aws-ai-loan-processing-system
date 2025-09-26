#!/usr/bin/env python3
"""
Script to update the decision making agent Lambda function
"""

import boto3

def update_decision_agent():
    """Update the decision making agent Lambda function"""
    try:
        # Initialize Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        
        print("📦 Updating decision-making-agent...")
        
        # Read the zip file
        with open('backend/lambda_functions/decision_agent/decision_agent.zip', 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Update the Lambda function
        response = lambda_client.update_function_code(
            FunctionName='decision-making-agent',
            ZipFile=zip_content
        )
        
        print(f"✅ Successfully updated decision-making-agent")
        print(f"   Version: {response['Version']}")
        print(f"   Last Modified: {response['LastModified']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating decision-making-agent: {str(e)}")
        return False

if __name__ == "__main__":
    update_decision_agent()
