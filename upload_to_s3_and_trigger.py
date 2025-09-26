#!/usr/bin/env python3
"""
Upload loan application forms to S3 and trigger the workflow
"""

import boto3
import json
import time
import uuid
import base64
from datetime import datetime

def upload_form_to_s3_and_trigger(form_file_path, applicant_name):
    """Upload a form to S3 and trigger the loan processing workflow"""
    
    print(f"🚀 Uploading {form_file_path} to S3 and triggering workflow...")
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
            print("📋 Final Output:")
            output = json.loads(exec_response['output'])
            print(json.dumps(output, indent=2))
            
            # Check DynamoDB for stored data
            print("\n🔍 Checking DynamoDB storage...")
            check_dynamodb_storage(applicant_id)
            
        else:
            print(f"❌ Workflow failed with status: {status}")
            if 'error' in exec_response:
                print(f"Error: {exec_response['error']}")
            if 'cause' in exec_response:
                print(f"Cause: {exec_response['cause']}")
    
    except Exception as e:
        print(f"❌ Error starting workflow: {str(e)}")

def check_dynamodb_storage(applicant_id):
    """Check if data was stored in DynamoDB"""
    
    dynamodb = boto3.client('dynamodb', region_name='us-east-1')
    
    # Check loan-decisions table
    try:
        decision_response = dynamodb.get_item(
            TableName='loan-decisions',
            Key={'application_id': {'S': applicant_id}}
        )
        
        if 'Item' in decision_response:
            print("✅ Loan decision found in DynamoDB:")
            print(json.dumps(decision_response['Item'], indent=2))
        else:
            print("❌ No loan decision found in DynamoDB")
    except Exception as e:
        print(f"❌ Error checking loan-decisions table: {e}")
    
    # Check risk-assessments table
    try:
        risk_response = dynamodb.get_item(
            TableName='risk-assessments',
            Key={'applicant_id': {'S': applicant_id}}
        )
        
        if 'Item' in risk_response:
            print("✅ Risk assessment found in DynamoDB:")
            print(json.dumps(risk_response['Item'], indent=2))
        else:
            print("❌ No risk assessment found in DynamoDB")
    except Exception as e:
        print(f"❌ Error checking risk-assessments table: {e}")

def main():
    """Main function to test both forms"""
    
    print("🚀 S3 Upload and Workflow Trigger Test")
    print("=" * 60)
    
    # Test Form 1
    print("\n📋 Testing Form 1: Michael Rodriguez")
    upload_form_to_s3_and_trigger(
        'sample_forms/loan_application_form_1.txt',
        'Michael Rodriguez'
    )
    
    print("\n" + "=" * 60)
    
    # Test Form 2
    print("\n📋 Testing Form 2: Emily Chen")
    upload_form_to_s3_and_trigger(
        'sample_forms/loan_application_form_2.txt',
        'Emily Chen'
    )
    
    print("\n✅ All tests completed!")

if __name__ == '__main__':
    main()
