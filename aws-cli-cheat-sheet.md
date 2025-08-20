# AWS CLI Cheat Sheet - Data Engineering Pipeline

*Commands used during the retail data pipeline project*

---

## 🔧 Initial Setup & Configuration

### Check AWS CLI Installation
```bash
aws --version
```

### Configure AWS Credentials
```bash
aws configure
# Prompts for:
# - AWS Access Key ID
# - AWS Secret Access Key  
# - Default region (e.g., us-east-1)
# - Default output format (json)
```

### Verify AWS Connection
```bash
aws sts get-caller-identity
# Returns: Account ID, User ARN, User ID
```

---

## 📁 S3 Storage Operations

### Create S3 Bucket
```bash
aws s3 mb s3://amit-choudhary-765432892721
```

### List All S3 Buckets
```bash
aws s3 ls
```

### Create Folders in S3 (using put-object)
```bash
aws s3api put-object --bucket amit-choudhary-765432892721 --key athena-results/
```

### Upload Single File to S3
```bash
aws s3 cp "C:\Users\amitr\Downloads\retail-gbmart-mathco dataset\customers.csv" s3://amit-choudhary-765432892721/raw-data/customers.csv
```

### Upload Multiple Files (Sync)
```bash
aws s3 sync "C:\Users\amitr\Downloads\retail-gbmart-mathco dataset\Fluctuate Inventories Json" s3://amit-choudhary-765432892721/raw-data/inventory/
```

### Move Files Within S3
```bash
aws s3 mv s3://amit-choudhary-765432892721/raw-data/customers.csv s3://amit-choudhary-765432892721/raw-data/csv/customers.csv
```

### List Files in S3 Bucket
```bash
# List root level
aws s3 ls s3://amit-choudhary-765432892721/

# List specific folder
aws s3 ls s3://amit-choudhary-765432892721/raw-data/

# List recursively with summary
aws s3 ls s3://amit-choudhary-765432892721/raw-data/ --recursive --summarize
```

### Copy File from S3 to Local (for inspection)
```bash
aws s3 cp s3://amit-choudhary-765432892721/raw-data/customers.csv - | head -3
```

### Delete Files from S3
```bash
aws s3 rm s3://amit-choudhary-765432892721/raw-data/csv/addresses/addresses.csv
```

---

## 🔐 IAM (Identity and Access Management)

### Create IAM Role
```bash
aws iam create-role \
    --role-name AWSGlueServiceRole-retail \
    --assume-role-policy-document '{
        "Version":"2012-10-17",
        "Statement":[{
            "Effect":"Allow",
            "Principal":{"Service":"glue.amazonaws.com"},
            "Action":"sts:AssumeRole"
        }]
    }' \
    --description "Service role for Glue crawler to access S3 data"
```

### Attach Policy to Role
```bash
aws iam attach-role-policy \
    --role-name AWSGlueServiceRole-retail \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole

aws iam attach-role-policy \
    --role-name AWSGlueServiceRole-retail \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

### List Roles (with filtering)
```bash
aws iam list-roles --query 'Roles[?contains(RoleName,`Glue`)].RoleName'
```

### Get Role Details
```bash
aws iam get-role --role-name AWSGlueServiceRole-retail
```

---

## 🗄️ AWS Glue Data Catalog

### Create Glue Database
```bash
aws glue create-database \
    --database-input Name=retail_db,Description="Retail data database for CSV and JSON files"
```

### Get Database Details
```bash
aws glue get-database --name retail_db
```

### Create Glue Crawler
```bash
aws glue create-crawler \
    --name retail-csv-crawler \
    --role arn:aws:iam::765432892721:role/AWSGlueServiceRole-retail \
    --database-name retail_db \
    --targets '{"S3Targets":[{"Path":"s3://amit-choudhary-765432892721/raw-data/","Exclusions":["s3://amit-choudhary-765432892721/raw-data/inventory/**"]}]}' \
    --description "Crawler for CSV files in retail dataset"
```

### Start Crawler
```bash
aws glue start-crawler --name retail-csv-crawler
```

### Check Crawler Status
```bash
aws glue get-crawler --name retail-csv-crawler --query 'Crawler.State'
```

### List Tables in Database
```bash
aws glue get-tables --database-name retail_db --query 'TableList[].Name'
```

### Get Table Details
```bash
aws glue get-table --database-name retail_db --name customers_csv
```

### Delete Table
```bash
aws glue delete-table --database-name retail_db --name customers_csv
```

### Delete Crawler
```bash
aws glue delete-crawler --name retail-csv-crawler
```

---

## 🔍 AWS Athena Queries

### Start Query Execution
```bash
aws athena start-query-execution \
    --query-string "CREATE DATABASE IF NOT EXISTS retail_db;" \
    --result-configuration OutputLocation=s3://amit-choudhary-765432892721/athena-results/
```

### Check Query Status
```bash
aws athena get-query-execution \
    --query-execution-id 045e456e-12b6-413a-8cb3-a7749196d064 \
    --query 'QueryExecution.Status.State'
```

### Get Query Results
```bash
aws athena get-query-results \
    --query-execution-id 045e456e-12b6-413a-8cb3-a7749196d064 \
    --query 'ResultSet.Rows[0:6]'
```

### Common Athena Queries via CLI

**Count Records:**
```bash
aws athena start-query-execution \
    --query-string "SELECT COUNT(*) as total_customers FROM retail_db.customers;" \
    --result-configuration OutputLocation=s3://amit-choudhary-765432892721/athena-results/
```

**Sample Data:**
```bash
aws athena start-query-execution \
    --query-string "SELECT customerid, firstname, lastname FROM retail_db.customers LIMIT 5;" \
    --result-configuration OutputLocation=s3://amit-choudhary-765432892721/athena-results/
```

**Create External Table:**
```bash
aws athena start-query-execution \
    --query-string "CREATE EXTERNAL TABLE retail_db.customers (
        customerid string, 
        firstname string, 
        lastname string, 
        email string, 
        phonenumber string, 
        dateofbirth string, 
        registrationdate string, 
        preferredpaymentmethodid string
    ) 
    ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe' 
    WITH SERDEPROPERTIES ('field.delim' = ',') 
    LOCATION 's3://amit-choudhary-765432892721/raw-data/csv/customers/' 
    TBLPROPERTIES ('skip.header.line.count'='1');" \
    --result-configuration OutputLocation=s3://amit-choudhary-765432892721/athena-results/
```

**Drop Table:**
```bash
aws athena start-query-execution \
    --query-string "DROP TABLE retail_db.customers;" \
    --result-configuration OutputLocation=s3://amit-choudhary-765432892721/athena-results/
```

---

## 🛠️ Advanced Operations

### List Athena Workgroups
```bash
aws athena list-work-groups
```

### Get Query Result with Specific Data
```bash
aws athena get-query-results \
    --query-execution-id QUERY_ID \
    --query 'ResultSet.Rows[1].Data[0].VarCharValue'
```

### Batch Operations with Variables
```bash
# Set variables
BUCKET_NAME="amit-choudhary-765432892721"
DATABASE_NAME="retail_db"
QUERY_ID="your-query-id"

# Use in commands
aws s3 ls s3://$BUCKET_NAME/
aws glue get-tables --database-name $DATABASE_NAME
```

---

## 🔄 Common Workflows

### Complete Pipeline Setup
```bash
# 1. Verify connection
aws sts get-caller-identity

# 2. Upload data
aws s3 cp "local-file.csv" s3://bucket/path/

# 3. Create database
aws glue create-database --database-input Name=retail_db

# 4. Create and run crawler
aws glue create-crawler --name my-crawler --role ROLE_ARN --database-name retail_db --targets 'S3Targets=[{Path="s3://bucket/path/"}]'
aws glue start-crawler --name my-crawler

# 5. Wait and check status
aws glue get-crawler --name my-crawler --query 'Crawler.State'

# 6. Query with Athena
aws athena start-query-execution --query-string "SELECT COUNT(*) FROM retail_db.table_name;" --result-configuration OutputLocation=s3://bucket/athena-results/
```

### Data Quality Check Workflow
```bash
# Check file uploaded correctly
aws s3 ls s3://bucket/path/ --summarize

# Verify crawler found the data
aws glue get-tables --database-name retail_db

# Test query
aws athena start-query-execution --query-string "SELECT * FROM retail_db.table_name LIMIT 1;" --result-configuration OutputLocation=s3://bucket/results/
```

---

## 💡 Pro Tips

### Using Profiles
```bash
# Configure multiple profiles
aws configure --profile production
aws configure --profile development

# Use specific profile
aws s3 ls --profile production
```

### Output Formats
```bash
# Table format (readable)
aws glue get-tables --database-name retail_db --output table

# Get specific values
aws glue get-tables --database-name retail_db --query 'TableList[].Name' --output text
```

### Combining Commands
```bash
# Get account ID and use in bucket name
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="my-bucket-$ACCOUNT_ID"
aws s3 mb s3://$BUCKET_NAME
```

### Error Handling
```bash
# Check if bucket exists before operations
if aws s3api head-bucket --bucket $BUCKET_NAME 2>/dev/null; then
    echo "Bucket exists"
else
    echo "Bucket not found"
fi
```

### Wait for Operations
```bash
# Wait for crawler to finish
while [ "$(aws glue get-crawler --name my-crawler --query 'Crawler.State' --output text)" = "RUNNING" ]; do
    echo "Waiting for crawler..."
    sleep 10
done
```

---

## 🚨 Common Issues & Solutions

### Permission Errors
```bash
# Check current identity
aws sts get-caller-identity

# Check if role exists
aws iam get-role --role-name AWSGlueServiceRole-retail

# List policies attached to role
aws iam list-attached-role-policies --role-name AWSGlueServiceRole-retail
```

### S3 Access Issues
```bash
# Test S3 access
aws s3 ls s3://bucket-name/

# Check bucket policy
aws s3api get-bucket-policy --bucket bucket-name
```

### Query Failures
```bash
# Check query execution details
aws athena get-query-execution --query-execution-id QUERY_ID

# Get error details
aws athena get-query-execution --query-execution-id QUERY_ID --query 'QueryExecution.Status.StateChangeReason'
```

---

## 📋 Environment Variables

```bash
# Useful environment variables
export AWS_DEFAULT_REGION=us-east-1
export AWS_DEFAULT_OUTPUT=json
export AWS_PAGER=""  # Disable pager for long outputs

# Use in scripts
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="my-data-lake-$ACCOUNT_ID"
```

---

## 🔍 Monitoring & Debugging

### CloudWatch Logs
```bash
# List log groups
aws logs describe-log-groups

# Get log events
aws logs get-log-events --log-group-name /aws/glue/crawlers --log-stream-name STREAM_NAME
```

### Cost Monitoring
```bash
# Get current month costs (requires Cost Explorer access)
aws ce get-cost-and-usage \
    --time-period Start=2025-08-01,End=2025-08-31 \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --group-by Type=DIMENSION,Key=SERVICE
```

---

*This cheat sheet covers all AWS CLI commands used during our data engineering pipeline project. Keep this handy for future AWS data projects!*

**Total Services Used:** S3, IAM, Glue, Athena  
**Total Commands:** 50+ variations  
**Use Case:** Complete data lake and analytics pipeline  

---

## 🎯 Quick Reference Summary

| **Task** | **Primary Command** |
|----------|-------------------|
| Upload data | `aws s3 cp` or `aws s3 sync` |
| Create crawler | `aws glue create-crawler` |
| Start crawler | `aws glue start-crawler` |
| Check status | `aws glue get-crawler` |
| Query data | `aws athena start-query-execution` |
| Get results | `aws athena get-query-results` |
| List tables | `aws glue get-tables` |
| Create role | `aws iam create-role` |