#!/usr/bin/env python3
"""
Simple script to upload a single form to S3 and trigger the workflow
Usage: python3 upload_single_form.py <form_file_path> <applicant_name>
"""

import sys
import boto3
import json
import time
import uuid
import base64
from datetime import datetime

def upload_single_form(form_file_path, applicant_name):
    """Upload a single form to S3 and trigger the workflow"""
    
    print(f"🚀 Uploading {form_file_path} for {applicant_name}")
    print("=" * 60)
    
    # Generate unique applicant ID
    applicant_id = str(uuid.uuid4())
    
    # Read the form file
    try:
        with open(form_file_path, 'r') as f:
            form_content = f.read()
    except Exception as e:
        print(f"❌ Error reading form file: {e}")
        return
    
    # Create S3 client
    s3_client = boto3.client('s3', region_name='us-east-1')
    bucket_name = 'ai-loan-docs-millionaire-20250923-01'
    
    # Upload form to S3
    s3_key = f'loan-applications/{applicant_id}/{applicant_name}_application.txt'
    
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=form_content.encode('utf-8'),
            ContentType='text/plain'
        )
        print(f"✅ Form uploaded to S3: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"❌ Error uploading to S3: {e}")
        return
    
    # Create workflow input
    workflow_input = {
        "applicant_id": applicant_id,
        "applicant_data": {
            "name": applicant_name,
            "email": f"{applicant_name.lower().replace(' ', '.')}@email.com",
            "phone": "+1-555-0000",
            "address": "123 Main St, City, State 12345",
            "date_of_birth": "1990-01-01",
            "ssn": "123-45-6789",
            "employment_status": "employed",
            "employer": "Sample Company",
            "annual_income": 75000,
            "monthly_expenses": 3000,
            "credit_score": 700,
            "existing_debt": 15000,
            "loan_purpose": "personal",
            "requested_amount": 50000,
            "loan_term_years": 5
        },
        "documents": [
            {
                "filename": f"{applicant_name}_application.txt",
                "content_type": "text/plain",
                "content": base64.b64encode(form_content.encode('utf-8')).decode('utf-8')
            }
        ],
        "start_time": datetime.utcnow().isoformat() + "Z"
    }
    
    # Get Step Functions client
    sfn_client = boto3.client('stepfunctions', region_name='us-east-1')
    
    # Get state machine ARN
    state_machines = sfn_client.list_state_machines()
    state_machine_arn = None
    
    for sm in state_machines['stateMachines']:
        if sm['name'] == 'ai-loan-processing-workflow':
            state_machine_arn = sm['stateMachineArn']
            break
    
    if not state_machine_arn:
        print("❌ State machine 'ai-loan-processing-workflow' not found!")
        return
    
    # Start execution
    execution_name = f"s3-upload-{applicant_id}-{int(time.time())}"
    
    try:
        print("🚀 Starting workflow execution...")
        response = sfn_client.start_execution(
            stateMachineArn=state_machine_arn,
            name=execution_name,
            input=json.dumps(workflow_input)
        )
        
        execution_arn = response['executionArn']
        print(f"📋 Execution ARN: {execution_arn}")
        
        # Monitor execution
        print("⏳ Monitoring execution...")
        while True:
            exec_response = sfn_client.describe_execution(executionArn=execution_arn)
            status = exec_response['status']
            
            print(f"📊 Status: {status}")
            
            if status != 'RUNNING':
                break
                
            time.sleep(5)
        
        print("=" * 60)
        
        if status == 'SUCCEEDED':
            print("✅ Workflow completed successfully!")
            print(f"📋 Applicant ID: {applicant_id}")
            print(f"👤 Applicant: {applicant_name}")
            print(f"📁 S3 Location: s3://{bucket_name}/{s3_key}")
            print(f"🔗 Step Functions: https://console.aws.amazon.com/states/home?region=us-east-1#/executions/details/{execution_arn}")
            
        else:
            print(f"❌ Workflow failed with status: {status}")
            if 'error' in exec_response:
                print(f"Error: {exec_response['error']}")
            if 'cause' in exec_response:
                print(f"Cause: {exec_response['cause']}")
    
    except Exception as e:
        print(f"❌ Error starting workflow: {str(e)}")

def main():
    """Main function"""
    
    if len(sys.argv) != 3:
        print("Usage: python3 upload_single_form.py <form_file_path> <applicant_name>")
        print("Example: python3 upload_single_form.py sample_forms/loan_application_form_1.txt 'John Doe'")
        sys.exit(1)
    
    form_file_path = sys.argv[1]
    applicant_name = sys.argv[2]
    
    upload_single_form(form_file_path, applicant_name)

if __name__ == '__main__':
    main()
