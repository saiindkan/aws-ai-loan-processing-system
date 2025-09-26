#!/usr/bin/env python3
"""
Script to update the Step Functions state machine with corrected workflow
"""

import boto3
import json

def update_step_functions():
    """Update the Step Functions state machine"""
    try:
        # Initialize Step Functions client
        stepfunctions = boto3.client('stepfunctions', region_name='us-east-1')
        
        print("📦 Updating Step Functions state machine...")
        
        # Read the updated workflow definition
        with open('infrastructure/step_functions/loan_processing_workflow.json', 'r') as f:
            workflow_definition = json.load(f)
        
        # Get the state machine ARN
        state_machines = stepfunctions.list_state_machines()
        workflow_arn = None
        
        for sm in state_machines['stateMachines']:
            if 'loan-processing' in sm['name'].lower():
                workflow_arn = sm['stateMachineArn']
                break
        
        if not workflow_arn:
            print("❌ Step Functions workflow not found")
            return False
        
        print(f"✅ Found workflow: {workflow_arn}")
        
        # Update the state machine
        response = stepfunctions.update_state_machine(
            stateMachineArn=workflow_arn,
            definition=json.dumps(workflow_definition)
        )
        
        print(f"✅ Successfully updated Step Functions state machine")
        print(f"   State Machine ARN: {response['stateMachineArn']}")
        print(f"   Last Updated: {response['updateDate']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Step Functions state machine: {str(e)}")
        return False

if __name__ == "__main__":
    update_step_functions()
