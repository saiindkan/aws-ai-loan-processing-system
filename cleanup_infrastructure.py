#!/usr/bin/env python3
"""
Cleanup Infrastructure Script
Removes all AWS resources created by the AI Loan Processing System
"""

import boto3
import time

def delete_lambda_functions():
    """Delete Lambda functions"""
    print("🗑️  Deleting Lambda functions...")
    
    lambda_client = boto3.client('lambda')
    
    functions = [
        'document-processing-agent',
        'risk-assessment-agent',
        'decision-making-agent'
    ]
    
    for func_name in functions:
        try:
            lambda_client.delete_function(FunctionName=func_name)
            print(f"✅ Deleted Lambda function: {func_name}")
        except lambda_client.exceptions.ResourceNotFoundException:
            print(f"⚠️  Lambda function {func_name} not found")
        except Exception as e:
            print(f"❌ Error deleting {func_name}: {e}")

def delete_step_functions_workflow():
    """Delete Step Functions workflow"""
    print("🗑️  Deleting Step Functions workflow...")
    
    sfn_client = boto3.client('stepfunctions')
    
    try:
        # List state machines
        response = sfn_client.list_state_machines()
        for sm in response['stateMachines']:
            if sm['name'] == 'ai-loan-processing-workflow':
                sfn_client.delete_state_machine(stateMachineArn=sm['stateMachineArn'])
                print("✅ Deleted Step Functions workflow")
                return
        
        print("⚠️  Step Functions workflow not found")
    except Exception as e:
        print(f"❌ Error deleting Step Functions workflow: {e}")

def delete_dynamodb_tables():
    """Delete DynamoDB tables"""
    print("🗑️  Deleting DynamoDB tables...")
    
    dynamodb = boto3.client('dynamodb')
    
    tables = ['loan-decisions', 'risk-assessments']
    
    for table_name in tables:
        try:
            dynamodb.delete_table(TableName=table_name)
            print(f"✅ Deleted DynamoDB table: {table_name}")
        except dynamodb.exceptions.ResourceNotFoundException:
            print(f"⚠️  DynamoDB table {table_name} not found")
        except Exception as e:
            print(f"❌ Error deleting {table_name}: {e}")
    
    # Wait for tables to be deleted
    print("⏳ Waiting for tables to be deleted...")
    for table_name in tables:
        try:
            while True:
                try:
                    dynamodb.describe_table(TableName=table_name)
                    time.sleep(2)
                except dynamodb.exceptions.ResourceNotFoundException:
                    break
            print(f"✅ Table {table_name} deleted")
        except Exception:
            pass

def delete_s3_bucket():
    """Delete S3 bucket and contents"""
    print("🗑️  Deleting S3 bucket...")
    
    s3 = boto3.client('s3')
    bucket_name = 'ai-loan-docs-millionaire-20250923-01'
    
    try:
        # List and delete all objects
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)
        
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
        
        # Delete bucket
        s3.delete_bucket(Bucket=bucket_name)
        print(f"✅ Deleted S3 bucket: {bucket_name}")
    except s3.exceptions.NoSuchBucket:
        print(f"⚠️  S3 bucket {bucket_name} not found")
    except Exception as e:
        print(f"❌ Error deleting S3 bucket: {e}")

def detach_iam_policies():
    """Detach IAM policies from roles"""
    print("🗑️  Detaching IAM policies...")
    
    iam = boto3.client('iam')
    
    roles_policies = [
        ('AILoanSageMakerExecutionRole', 'arn:aws:iam::aws:policy/AmazonSageMakerFullAccess'),
        ('AILoanLambdaExecutionRole', 'arn:aws:iam::aws:policy/service-role/AWSLambda_FullAccess'),
        ('AILoanStepFunctionsExecutionRole', 'arn:aws:iam::aws:policy/service-role/AWSLambda_FullAccess')
    ]
    
    for role_name, policy_arn in roles_policies:
        try:
            iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
            print(f"✅ Detached policy from {role_name}")
        except iam.exceptions.NoSuchEntityException:
            print(f"⚠️  Role {role_name} not found")
        except Exception as e:
            print(f"❌ Error detaching policy from {role_name}: {e}")

def delete_iam_roles():
    """Delete IAM roles"""
    print("🗑️  Deleting IAM roles...")
    
    iam = boto3.client('iam')
    
    roles = [
        'AILoanSageMakerExecutionRole',
        'AILoanLambdaExecutionRole',
        'AILoanStepFunctionsExecutionRole'
    ]
    
    for role_name in roles:
        try:
            iam.delete_role(RoleName=role_name)
            print(f"✅ Deleted IAM role: {role_name}")
        except iam.exceptions.NoSuchEntityException:
            print(f"⚠️  IAM role {role_name} not found")
        except Exception as e:
            print(f"❌ Error deleting {role_name}: {e}")

def main():
    """Main cleanup function"""
    print("🧹 AWS AI Loan Processing System - Cleanup")
    print("=" * 50)
    print("⚠️  WARNING: This will delete ALL resources!")
    print("This includes:")
    print("- Lambda functions")
    print("- Step Functions workflow")
    print("- DynamoDB tables (and all data)")
    print("- S3 bucket (and all files)")
    print("- IAM roles and policies")
    print()
    
    confirm = input("Are you sure you want to continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Cleanup cancelled")
        return
    
    try:
        # Check AWS credentials
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS Account: {identity['Account']}")
        print(f"✅ User: {identity['Arn']}")
        print()
        
        # Cleanup resources
        delete_lambda_functions()
        print()
        
        delete_step_functions_workflow()
        print()
        
        delete_dynamodb_tables()
        print()
        
        delete_s3_bucket()
        print()
        
        detach_iam_policies()
        print()
        
        delete_iam_roles()
        print()
        
        print("🎉 Cleanup complete!")
        print("All resources have been removed from your AWS account.")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        print("Please check your AWS credentials and permissions")

if __name__ == '__main__':
    main()
