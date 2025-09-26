#!/usr/bin/env python3
"""
Script to run the complete Step Functions workflow and verify DynamoDB storage
"""

import boto3
import json
import uuid
import time
from datetime import datetime

def create_test_workflow_input():
    """Create test input for the Step Functions workflow"""
    test_input = {
        "applicant_id": str(uuid.uuid4()),
        "applicant_data": {
            "name": "Jane Smith",
            "email": "jane.smith@email.com",
            "phone": "+1-555-0123",
            "address": "123 Main St, Anytown, USA",
            "date_of_birth": "1985-06-15",
            "ssn": "123-45-6789",
            "employment_status": "employed",
            "employer": "Tech Corp Inc",
            "annual_income": 75000,
            "monthly_expenses": 2500,
            "credit_score": 720,
            "existing_debt": 15000,
            "loan_purpose": "home_purchase",
            "requested_amount": 300000,
            "loan_term_years": 30
        },
        "documents": [
            {
                "filename": "bank_statement.pdf",
                "content": "JVBERi0xLjQKJcOkw7zDtsO8CjIgMCBvYmoKPDwKL0xlbmd0aCAzIDAgUgo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjAgMCBUZAooQmFuayBTdGF0ZW1lbnQpIFRqCkVUCkJUCi9GMSAxMCBUZgowIDAgVGQKKERhdGU6IDEyLzAxLzIwMjQpIFRqCkVUCkJUCi9GMSAxMCBUZgowIDAgVGQKKEluY29tZTogJDcsNTAwLjAwKSBUagpFVApCVAovRjEgMTAgVGYKMCAwIFRkCihFeHBlbnNlczogJDIsNTAwLjAwKSBUagpFVApCVAovRjEgMTAgVGYKMCAwIFRkCihCYWxhbmNlOiAkMjUsMDAwLjAwKSBUagpFVApFbmRzdHJlYW0KZW5kb2JqCjMgMCBvYmoKNDUKZW5kb2JqCjEgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCA0IDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSAyIDAgUgo+Pgo+PgovQ29udGVudHMgMiAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFsxIDAgUl0KL0NvdW50IDEKPj4KZW5kb2JqCjUgMCBvYmoKPDwKL1R5cGUgL0NhdGFsb2cKL1BhZ2VzIDQgMCBSCj4+CmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDAxOCAwMDAwMCBuIAowMDAwMDAwMDc3IDAwMDAwIG4gCjAwMDAwMDAxMjMgMDAwMDAgbiAKMDAwMDAwMDI0OCAwMDAwMCBuIAowMDAwMDAwMzI3IDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgNgovUm9vdCA1IDAgUgovSW5mbyA2IDAgUgo+PgpzdGFydHhyZWYKNDIzCiUlRU9G",
                "content_type": "application/pdf"
            },
            {
                "filename": "pay_stub.pdf",
                "content": "JVBERi0xLjQKJcOkw7zDtsO8CjIgMCBvYmoKPDwKL0xlbmd0aCAzIDAgUgo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjAgMCBUZAooUGF5IFN0dWIpIFRqCkVUCkJUCi9GMSAxMCBUZgowIDAgVGQKKERhdGU6IDEyLzAxLzIwMjQpIFRqCkVUCkJUCi9GMSAxMCBUZgowIDAgVGQKKFNhbGFyeTogJDcsNTAwLjAwKSBUagpFVApCVAovRjEgMTAgVGYKMCAwIFRkCihUYXhlczogJDEsNTAwLjAwKSBUagpFVApCVAovRjEgMTAgVGYKMCAwIFRkCihOZXQgUGF5OiAkNiwwMDAuMDApIFRqCkVUCkVuZHN0cmVhbQplbmRvYmoKMyAwIG9iago0NQplbmRvYmoKMSAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDQgMCBSCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCi9SZXNvdXJjZXMgPDwKL0ZvbnQgPDwKL0YxIDIgMCBSCj4+Cj4+Ci9Db250ZW50cyAyIDAgUgo+PgplbmRvYmoKNCAwIG9iago8PAovVHlwZSAvUGFnZXMKL0tpZHMgWzEgMCBSXQovQ291bnQgMQo+PgplbmRvYmoKNSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgNCAwIFIKPj4KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAwOSAwMDAwMCBuIAowMDAwMDAwMDE4IDAwMDAwIG4gCjAwMDAwMDAwNzcgMDAwMDAgbiAKMDAwMDAwMDEyMyAwMDAwMCBuIAowMDAwMDAwMjQ4IDAwMDAwIG4gCjAwMDAwMDAzMjcgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZSA2Ci9Sb290IDUgMCBSCi9JbmZvIDYgMCBSCj4+CnN0YXJ0eHJlZgo0MjMKJSVFT0Y=",
                "content_type": "application/pdf"
            }
        ]
    }
    
    return test_input

def run_step_functions_workflow():
    """Run the Step Functions workflow"""
    try:
        # Initialize Step Functions client
        stepfunctions = boto3.client('stepfunctions', region_name='us-east-1')
        
        # Get the state machine ARN
        state_machines = stepfunctions.list_state_machines()
        workflow_arn = None
        
        for sm in state_machines['stateMachines']:
            if 'loan-processing' in sm['name'].lower():
                workflow_arn = sm['stateMachineArn']
                break
        
        if not workflow_arn:
            print("❌ Step Functions workflow not found")
            return None
        
        print(f"✅ Found workflow: {workflow_arn}")
        
        # Create test input
        test_input = create_test_workflow_input()
        applicant_id = test_input['applicant_id']
        
        print(f"🚀 Starting workflow execution for applicant: {applicant_id}")
        print("=" * 60)
        
        # Start execution
        execution_response = stepfunctions.start_execution(
            stateMachineArn=workflow_arn,
            name=f"loan-processing-{applicant_id}-{int(time.time())}",
            input=json.dumps(test_input)
        )
        
        execution_arn = execution_response['executionArn']
        print(f"📋 Execution ARN: {execution_arn}")
        
        # Monitor execution
        print("⏳ Monitoring workflow execution...")
        max_wait_time = 300  # 5 minutes
        wait_time = 0
        
        while wait_time < max_wait_time:
            execution_details = stepfunctions.describe_execution(
                executionArn=execution_arn
            )
            
            status = execution_details['status']
            print(f"📊 Status: {status}")
            
            if status == 'SUCCEEDED':
                print("✅ Workflow completed successfully!")
                print("=" * 60)
                
                # Get execution output
                output = json.loads(execution_details['output'])
                print("📋 Workflow Output:")
                print(json.dumps(output, indent=2, default=str))
                
                return applicant_id, output
                
            elif status == 'FAILED':
                print("❌ Workflow failed!")
                print("=" * 60)
                
                # Get failure details
                if 'error' in execution_details:
                    print(f"Error: {execution_details['error']}")
                if 'cause' in execution_details:
                    print(f"Cause: {execution_details['cause']}")
                
                return None, None
                
            elif status == 'TIMED_OUT':
                print("⏰ Workflow timed out!")
                return None, None
                
            elif status == 'ABORTED':
                print("🛑 Workflow aborted!")
                return None, None
            
            # Wait before checking again
            time.sleep(10)
            wait_time += 10
            print(f"⏳ Waiting... ({wait_time}s elapsed)")
        
        print("⏰ Workflow monitoring timed out")
        return None, None
        
    except Exception as e:
        print(f"❌ Error running Step Functions workflow: {str(e)}")
        return None, None

def verify_dynamodb_storage(applicant_id):
    """Verify that data was stored in DynamoDB"""
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        print(f"\n🔍 Verifying DynamoDB storage for applicant: {applicant_id}")
        print("=" * 60)
        
        # Check loan-decisions table
        print("📋 Checking loan-decisions table...")
        try:
            loan_response = dynamodb.get_item(
                TableName='loan-decisions',
                Key={
                    'application_id': {'S': applicant_id}
                }
            )
            
            if 'Item' in loan_response:
                print("✅ Loan decision found in DynamoDB!")
                
                # Parse and display the item
                item = loan_response['Item']
                parsed_item = {}
                for key, value in item.items():
                    if 'S' in value:
                        parsed_item[key] = value['S']
                    elif 'N' in value:
                        parsed_item[key] = value['N']
                    elif 'BOOL' in value:
                        parsed_item[key] = value['BOOL']
                    else:
                        parsed_item[key] = value
                
                print("📊 Loan Decision Data:")
                print(json.dumps(parsed_item, indent=2, default=str))
                
            else:
                print("❌ No loan decision found in DynamoDB")
                
        except Exception as e:
            print(f"❌ Error checking loan-decisions table: {str(e)}")
        
        # Check risk-assessments table
        print("\n📋 Checking risk-assessments table...")
        try:
            risk_response = dynamodb.get_item(
                TableName='risk-assessments',
                Key={
                    'applicant_id': {'S': applicant_id}
                }
            )
            
            if 'Item' in risk_response:
                print("✅ Risk assessment found in DynamoDB!")
                
                # Parse and display the item
                item = risk_response['Item']
                parsed_item = {}
                for key, value in item.items():
                    if 'S' in value:
                        parsed_item[key] = value['S']
                    elif 'N' in value:
                        parsed_item[key] = value['N']
                    elif 'BOOL' in value:
                        parsed_item[key] = value['BOOL']
                    elif 'L' in value:
                        parsed_item[key] = [v['S'] for v in value['L']]
                    else:
                        parsed_item[key] = value
                
                print("📊 Risk Assessment Data:")
                print(json.dumps(parsed_item, indent=2, default=str))
                
            else:
                print("❌ No risk assessment found in DynamoDB")
                
        except Exception as e:
            print(f"❌ Error checking risk-assessments table: {str(e)}")
        
        print("\n✅ DynamoDB verification complete!")
        
    except Exception as e:
        print(f"❌ Error verifying DynamoDB storage: {str(e)}")

def main():
    """Main function to run the complete workflow"""
    print("🚀 Complete Step Functions Workflow Runner")
    print("=" * 60)
    
    # Run the Step Functions workflow
    applicant_id, workflow_output = run_step_functions_workflow()
    
    if applicant_id:
        # Verify DynamoDB storage
        verify_dynamodb_storage(applicant_id)
        
        print("\n🎉 Complete workflow execution successful!")
        print(f"📋 Applicant ID: {applicant_id}")
        print("✅ Data has been processed and stored in DynamoDB")
        
    else:
        print("\n❌ Workflow execution failed")
        print("💡 Check the error messages above for details")

if __name__ == "__main__":
    main()
