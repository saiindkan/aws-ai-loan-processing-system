# AWS AI-Powered Loan Processing System - Setup Guide

## 🚀 **Quick Start Guide**

This guide will help you set up and run the AI-powered loan processing system on your own AWS account.

## 📋 **Prerequisites**

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Python 3.9+** installed
4. **Git** installed

## 🔧 **Step 1: Clone the Repository**

```bash
git clone <your-repository-url>
cd aws-ai-loan-system
```

## 🔑 **Step 2: Configure AWS Credentials**

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region: `us-east-1`
- Default output format: `json`

## 🏗️ **Step 3: Deploy Infrastructure**

Run the automated setup script:

```bash
python3 setup_infrastructure.py
```

This script will:
- Create IAM roles and policies
- Create Lambda functions
- Create DynamoDB tables
- Create Step Functions workflow
- Create S3 bucket

## 🧪 **Step 4: Test the System**

### Test 1: Manual Workflow Test
```bash
python3 test_manual_workflow.py
```

### Test 2: S3 Upload Test
```bash
python3 upload_single_form.py sample_forms/loan_application_saibhargav.txt "Sai Bhargav"
```

### Test 3: View Results
```bash
python3 view_dynamodb_data.py
```

## 📊 **Step 5: View Your Data**

### DynamoDB Console
1. Go to [AWS DynamoDB Console](https://console.aws.amazon.com/dynamodb/)
2. Select `loan-decisions` table
3. Click "Explore table items"

### Step Functions Console
1. Go to [AWS Step Functions Console](https://console.aws.amazon.com/states/)
2. Select `ai-loan-processing-workflow`
3. View execution history

## 🎯 **Sample Applications**

The system includes sample loan application forms:
- `sample_forms/loan_application_form_1.txt` - Michael Rodriguez
- `sample_forms/loan_application_form_2.txt` - Emily Chen
- `sample_forms/loan_application_saibhargav.txt` - Sai Bhargav

## 🔍 **Troubleshooting**

### Common Issues:

1. **AWS CLI not found**
   ```bash
   pip install awscli
   ```

2. **Permission denied**
   - Ensure your AWS user has necessary permissions
   - Check IAM policies

3. **Region issues**
   - Ensure you're using `us-east-1` region
   - Update region in scripts if needed

4. **Lambda timeout**
   - Check CloudWatch logs
   - Increase timeout if needed

## 📈 **Monitoring**

### CloudWatch Logs
- Document Processing: `/aws/lambda/document-processing-agent`
- Risk Assessment: `/aws/lambda/risk-assessment-agent`
- Decision Making: `/aws/lambda/decision-making-agent`

### Step Functions
- Monitor workflow executions
- View execution history
- Check for errors

## 🧹 **Cleanup**

To remove all resources:
```bash
python3 cleanup_infrastructure.py
```

## 📚 **Architecture Overview**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   S3 Upload     │───▶│  Step Functions  │───▶│   DynamoDB      │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Lambda Agents  │
                       │                  │
                       │ 1. Document      │
                       │ 2. Risk          │
                       │ 3. Decision      │
                       └──────────────────┘
```

## 🎉 **Success!**

Once setup is complete, you'll have:
- ✅ AI-powered loan processing system
- ✅ Document analysis with AWS Textract
- ✅ Risk assessment with ML models
- ✅ Automated decision making
- ✅ Data storage in DynamoDB
- ✅ Complete workflow orchestration

## 📞 **Support**

For issues or questions:
1. Check the troubleshooting section
2. Review AWS CloudWatch logs
3. Verify IAM permissions
4. Check Step Functions execution history

---

**Happy Processing! 🚀**
