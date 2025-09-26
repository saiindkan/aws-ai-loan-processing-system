#!/usr/bin/env python3
"""
Automated Infrastructure Setup Script
Sets up the complete AWS AI Loan Processing System
"""

import boto3
import json
import time
import os
import zipfile
from datetime import datetime

def create_iam_roles():
    """Create IAM roles for the system"""
    print("🔧 Creating IAM roles...")
    
    iam = boto3.client('iam')
    
    # SageMaker Role
    try:
        with open('sagemaker-trust.json', 'r') as f:
            trust_policy = f.read()
        
        iam.create_role(
            RoleName='AILoanSageMakerExecutionRole',
            AssumeRolePolicyDocument=trust_policy,
            Description='Role for SageMaker execution in AI Loan System'
        )
        print("✅ Created SageMaker role")
    except iam.exceptions.EntityAlreadyExistsException:
        print("⚠️  SageMaker role already exists")
    
    # Lambda Role
    try:
        with open('lambda-trust.json', 'r') as f:
            trust_policy = f.read()
        
        iam.create_role(
            RoleName='AILoanLambdaExecutionRole',
            AssumeRolePolicyDocument=trust_policy,
            Description='Role for Lambda execution in AI Loan System'
        )
        print("✅ Created Lambda role")
    except iam.exceptions.EntityAlreadyExistsException:
        print("⚠️  Lambda role already exists")
    
    # Step Functions Role
    try:
        with open('infrastructure/step_functions/stepfunctions-trust.json', 'r') as f:
            trust_policy = f.read()
        
        iam.create_role(
            RoleName='AILoanStepFunctionsExecutionRole',
            AssumeRolePolicyDocument=trust_policy,
            Description='Role for Step Functions execution in AI Loan System'
        )
        print("✅ Created Step Functions role")
    except iam.exceptions.EntityAlreadyExistsException:
        print("⚠️  Step Functions role already exists")
    
    # Attach policies
    policies = [
        ('AILoanSageMakerExecutionRole', 'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'),
        ('AILoanLambdaExecutionRole', 'arn:aws:iam::aws:policy/service-role/AWSLambda_FullAccess'),
        ('AILoanStepFunctionsExecutionRole', 'arn:aws:iam::aws:policy/service-role/AWSLambda_FullAccess')
    ]
    
    for role_name, policy_arn in policies:
        try:
            iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
            print(f"✅ Attached policy to {role_name}")
        except Exception as e:
            print(f"⚠️  Policy attachment warning: {e}")

def create_dynamodb_tables():
    """Create DynamoDB tables"""
    print("🗄️  Creating DynamoDB tables...")
    
    dynamodb = boto3.client('dynamodb')
    
    tables = [
        {
            'TableName': 'loan-decisions',
            'KeySchema': [
                {'AttributeName': 'application_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'application_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'risk-assessments',
            'KeySchema': [
                {'AttributeName': 'applicant_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'applicant_id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
    ]
    
    for table in tables:
        try:
            dynamodb.create_table(**table)
            print(f"✅ Created table: {table['TableName']}")
        except dynamodb.exceptions.ResourceInUseException:
            print(f"⚠️  Table {table['TableName']} already exists")
    
    # Wait for tables to be active
    print("⏳ Waiting for tables to be active...")
    for table_name in ['loan-decisions', 'risk-assessments']:
        while True:
            response = dynamodb.describe_table(TableName=table_name)
            if response['Table']['TableStatus'] == 'ACTIVE':
                break
            time.sleep(2)
        print(f"✅ Table {table_name} is active")

def create_s3_bucket():
    """Create S3 bucket for documents"""
    print("🪣 Creating S3 bucket...")
    
    s3 = boto3.client('s3')
    bucket_name = 'ai-loan-docs-millionaire-20250923-01'
    
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"✅ Created S3 bucket: {bucket_name}")
    except s3.exceptions.BucketAlreadyExists:
        print(f"⚠️  S3 bucket {bucket_name} already exists")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"⚠️  S3 bucket {bucket_name} already owned by you")

def create_lambda_functions():
    """Create Lambda functions"""
    print("⚡ Creating Lambda functions...")
    
    lambda_client = boto3.client('lambda')
    iam = boto3.client('iam')
    
    # Get role ARN
    try:
        role_response = iam.get_role(RoleName='AILoanLambdaExecutionRole')
        role_arn = role_response['Role']['Arn']
    except Exception as e:
        print(f"❌ Error getting Lambda role: {e}")
        return
    
    functions = [
        {
            'name': 'document-processing-agent',
            'handler': 'lambda_function.lambda_handler',
            'runtime': 'python3.9',
            'timeout': 300,
            'memory': 512
        },
        {
            'name': 'risk-assessment-agent',
            'handler': 'lambda_function.lambda_handler',
            'runtime': 'python3.9',
            'timeout': 300,
            'memory': 512
        },
        {
            'name': 'decision-making-agent',
            'handler': 'lambda_function.lambda_handler',
            'runtime': 'python3.9',
            'timeout': 300,
            'memory': 512
        }
    ]
    
    for func in functions:
        try:
            # Create deployment package
            zip_path = f"backend/lambda_functions/{func['name'].replace('-', '_')}/{func['name']}.zip"
            
            if os.path.exists(zip_path):
                with open(zip_path, 'rb') as f:
                    zip_content = f.read()
            else:
                # Create a simple zip with just the lambda function
                zip_content = create_simple_zip(func['name'])
            
            # Create function
            lambda_client.create_function(
                FunctionName=func['name'],
                Runtime=func['runtime'],
                Role=role_arn,
                Handler=func['handler'],
                Code={'ZipFile': zip_content},
                Timeout=func['timeout'],
                MemorySize=func['memory'],
                Description=f'AI Loan System - {func["name"]}'
            )
            print(f"✅ Created Lambda function: {func['name']}")
            
        except lambda_client.exceptions.ResourceConflictException:
            print(f"⚠️  Lambda function {func['name']} already exists")
        except Exception as e:
            print(f"❌ Error creating {func['name']}: {e}")

def create_simple_zip(function_name):
    """Create a simple zip file for Lambda function"""
    import io
    
    # Simple lambda function code
    code = f'''
import json
import boto3
from datetime import datetime

def lambda_handler(event, context):
    return {{
        'statusCode': 200,
        'body': json.dumps({{
            'message': 'Hello from {function_name}',
            'timestamp': datetime.utcnow().isoformat()
        }})
    }}
'''
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('lambda_function.py', code)
    
    return zip_buffer.getvalue()

def create_step_functions_workflow():
    """Create Step Functions workflow"""
    print("🔄 Creating Step Functions workflow...")
    
    sfn_client = boto3.client('stepfunctions')
    iam = boto3.client('iam')
    
    # Get role ARN
    try:
        role_response = iam.get_role(RoleName='AILoanStepFunctionsExecutionRole')
        role_arn = role_response['Role']['Arn']
    except Exception as e:
        print(f"❌ Error getting Step Functions role: {e}")
        return
    
    # Read workflow definition
    try:
        with open('infrastructure/step_functions/loan_processing_workflow.json', 'r') as f:
            definition = f.read()
    except Exception as e:
        print(f"❌ Error reading workflow definition: {e}")
        return
    
    try:
        sfn_client.create_state_machine(
            name='ai-loan-processing-workflow',
            definition=definition,
            roleArn=role_arn
        )
        print("✅ Created Step Functions workflow")
    except sfn_client.exceptions.StateMachineAlreadyExists:
        print("⚠️  Step Functions workflow already exists")

def main():
    """Main setup function"""
    print("🚀 AWS AI Loan Processing System - Infrastructure Setup")
    print("=" * 60)
    
    try:
        # Check AWS credentials
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Account: {identity['Account']}")
        print(f"✅ User: {identity['Arn']}")
        print()
        
        # Setup infrastructure
        create_iam_roles()
        print()
        
        create_dynamodb_tables()
        print()
        
        create_s3_bucket()
        print()
        
        create_lambda_functions()
        print()
        
        create_step_functions_workflow()
        print()
        
        print("🎉 Infrastructure setup complete!")
        print("=" * 60)
        print("Next steps:")
        print("1. Run: python3 test_manual_workflow.py")
        print("2. Run: python3 upload_single_form.py sample_forms/loan_application_saibhargav.txt 'Sai Bhargav'")
        print("3. Run: python3 view_dynamodb_data.py")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("Please check your AWS credentials and permissions")

if __name__ == '__main__':
    main()
