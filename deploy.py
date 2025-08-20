#!/usr/bin/env python3
"""
Deployment script for AWS Data Pipeline
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return None

def main():
    """Main deployment function"""
    print("🚀 Starting AWS Data Pipeline Deployment")
    
    # Check if AWS CLI is configured
    result = run_command("aws sts get-caller-identity", "Checking AWS credentials")
    if not result:
        print("❌ AWS credentials not configured. Please run 'aws configure' first.")
        sys.exit(1)
    
    print(f"📋 AWS Account: {result}")
    
    # Install Python dependencies
    run_command("pip install -r requirements.txt", "Installing Python dependencies")
    
    # Bootstrap CDK (if not already done)
    run_command("cdk bootstrap", "Bootstrapping CDK environment")
    
    # Synthesize CloudFormation templates
    run_command("cdk synth", "Synthesizing CloudFormation templates")
    
    # Deploy the stack
    deploy_result = run_command("cdk deploy --require-approval never", "Deploying data pipeline stack")
    
    if deploy_result:
        print("\n🎉 Deployment completed successfully!")
        print("\n📊 Your data pipeline includes:")
        print("• S3 buckets for raw and processed data")
        print("• Lambda function for data processing")
        print("• EventBridge rule for automated triggering")
        print("• Glue database and crawler for metadata")
        print("\n📝 Next steps:")
        print("1. Upload CSV/JSON files to the raw data bucket")
        print("2. Check processed data in the processed bucket")
        print("3. Query metadata using AWS Glue Data Catalog")
    else:
        print("\n❌ Deployment failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()