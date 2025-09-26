#!/usr/bin/env python3
"""
Manual Test Script for AI Loan Processing System
Tests the complete workflow with custom data
"""

import boto3
import json
import time
import uuid
import base64
from datetime import datetime

def create_sample_loan_application():
    """Create a sample loan application for testing"""
    
    # Generate unique applicant ID
    applicant_id = str(uuid.uuid4())
    
    # Sample loan application data
    loan_application = {
        "applicant_id": applicant_id,
        "applicant_data": {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@email.com",
            "phone": "+1-555-0199",
            "address": "456 Oak Street, Springfield, IL 62701",
            "date_of_birth": "1988-03-22",
            "ssn": "987-65-4321",
            "employment_status": "employed",
            "employer": "Springfield Tech Solutions",
            "annual_income": 85000,
            "monthly_expenses": 3200,
            "credit_score": 780,
            "existing_debt": 12000,
            "loan_purpose": "home_improvement",
            "requested_amount": 75000,
            "loan_term_years": 5
        },
        "documents": [
            {
                "filename": "bank_statement_sarah.pdf",
                "content_type": "application/pdf",
                "content": base64.b64encode(b"""
Bank Statement - Sarah Johnson
Account: ****1234
Date: 12/01/2024

Beginning Balance: $15,000.00
Deposits:
- Salary Deposit: $7,083.33
- Bonus: $2,000.00
- Interest: $45.67

Withdrawals:
- Mortgage Payment: $1,800.00
- Car Payment: $450.00
- Utilities: $180.00
- Groceries: $320.00
- Gas: $120.00
- Insurance: $200.00

Ending Balance: $21,279.00

Monthly Income: $7,083.33
Monthly Expenses: $3,070.00
Net Monthly: $4,013.33
                """).decode('utf-8')
            },
            {
                "filename": "pay_stub_sarah.pdf",
                "content_type": "application/pdf",
                "content": base64.b64encode(b"""
Pay Stub - Sarah Johnson
Springfield Tech Solutions
Pay Period: 11/16/2024 - 11/30/2024

Employee ID: 12345
SSN: ***-**-4321

Earnings:
- Regular Hours: 80 @ $45.00 = $3,600.00
- Overtime: 8 @ $67.50 = $540.00
- Bonus: $1,500.00
- Total Gross: $5,640.00

Deductions:
- Federal Tax: $1,128.00
- State Tax: $282.00
- Social Security: $349.68
- Medicare: $81.78
- Health Insurance: $150.00
- 401(k): $564.00
- Total Deductions: $2,555.46

Net Pay: $3,084.54

YTD Gross: $67,680.00
YTD Net: $37,014.48
                """).decode('utf-8')
            }
        ],
        "start_time": datetime.utcnow().isoformat() + "Z"
    }
    
    return loan_application

def test_workflow_manually():
    """Test the workflow manually with custom data"""
    
    print("🚀 Manual Loan Processing Test")
    print("=" * 50)
    
    # Create sample application
    application = create_sample_loan_application()
    applicant_id = application["applicant_id"]
    
    print(f"📋 Testing with applicant: {applicant_id}")
    print(f"👤 Applicant: {application['applicant_data']['name']}")
    print(f"💰 Loan Amount: ${application['applicant_data']['requested_amount']:,}")
    print(f"📊 Credit Score: {application['applicant_data']['credit_score']}")
    print(f"💼 Annual Income: ${application['applicant_data']['annual_income']:,}")
    print()
    
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
    
    print(f"✅ Found state machine: {state_machine_arn}")
    
    # Start execution
    execution_name = f"manual-test-{applicant_id}-{int(time.time())}"
    
    try:
        print("🚀 Starting workflow execution...")
        response = sfn_client.start_execution(
            stateMachineArn=state_machine_arn,
            name=execution_name,
            input=json.dumps(application)
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
        
        print("=" * 50)
        
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

if __name__ == '__main__':
    test_workflow_manually()
