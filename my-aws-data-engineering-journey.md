# My AWS Data Engineering Journey: From Zero to Querying Retail Data

*A beginner's hands-on experience building data pipelines on AWS*

---

## The Goal

As a complete beginner in AWS Data Engineering, I set out with a simple but ambitious goal: **build a data pipeline on AWS that could ingest, store, and query real retail data**. I had a retail dataset with customer information, product catalogs, address data, and daily inventory records across 5 warehouses - perfect for learning data engineering concepts.

My vision was to:
- Upload my data to AWS S3
- Set up proper data cataloging
- Query the data using SQL through AWS Athena
- Learn AWS services hands-on, step by step

## The Dataset

I started with the **retail-gbmart-mathco dataset** containing:
- **3 CSV files**: customers.csv (customer data), products.csv (product catalog), addresses.csv (customer addresses)
- **150 JSON files**: Daily inventory data for 5 warehouses over 30 days
- **Total size**: ~112 MB of real-world retail data

Perfect for learning - complex enough to be realistic, small enough to manage costs.

## Chapter 1: Setting Up AWS Infrastructure

### The Foundation
My first step was setting up AWS CLI and configuring credentials. This seemed straightforward until I hit my first challenge - **permissions**.

**Challenge #1: AWS Permissions**
Initially, my `temp-user` account couldn't create S3 buckets. I learned about IAM policies the hard way:
- Started with basic S3 permissions
- Escalated to AmazonS3FullAccess
- Eventually needed AthenaFullAccess and Glue permissions
- Finally settled on AdministratorAccess for learning

**Learning**: AWS permissions are granular and service-specific. Start broad for learning, then narrow down in production.

### Creating the Data Lake Structure
I decided to organize everything under a single S3 bucket: `amit-choudhary-765432892721`

```
s3://amit-choudhary-765432892721/
├── raw-data/          # Source data
├── athena-results/    # Query results
├── processed-data/    # Future processed files
└── glue-scripts/      # ETL scripts
```

This taught me the importance of **data lake organization** from day one.

## Chapter 2: Data Ingestion - The Upload Marathon

### The CSV Upload Victory
Uploading the 3 CSV files was smooth:
- customers.csv (1.8MB) ✅
- products.csv (100MB) ✅ 
- addresses.csv (3MB) ✅

### The JSON Upload Challenge
Then came the 150 JSON inventory files. I learned about the `aws s3 sync` command:

```bash
aws s3 sync "local-inventory-folder" s3://amit-choudhary-765432892721/raw-data/inventory/
```

Watching 150 files upload in parallel was satisfying! **Total uploaded: 153 files, ~112MB**.

**Learning**: AWS CLI's `sync` command is powerful for batch uploads. Much better than uploading files one by one.

## Chapter 3: The Athena Setup Odyssey

### Challenge #2: Service Roles and Permissions
Setting up AWS Athena to query my data taught me about **service roles**. Unlike user permissions, AWS services need their own identities to access resources.

I had to create a **Glue Service Role** for the data catalog:
```bash
aws iam create-role --role-name AWSGlueServiceRole-retail --assume-role-policy-document '{...}'
aws iam attach-role-policy --role-name AWSGlueServiceRole-retail --policy-arn arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole
```

**Learning**: Services like Glue crawlers need service roles, not user permissions. This is a key AWS security concept.

### The Data Catalog Creation
I used AWS Glue to automatically catalog my CSV files:

1. **Created Glue Database**: `retail_db`
2. **Created Glue Crawler**: Scanned my S3 data and inferred schemas
3. **Generated Tables**: Automatically created table definitions

The crawler found my data and created tables, but then I hit my biggest challenge...

## Chapter 4: The Great Data Organization Challenge

### Challenge #3: Mixed Data Nightmare
My first Athena query returned **798,842 rows** for "customers" but the results looked like this:
```
customerid: FSJ-186996
firstname: magnetic pin set of 2 pairs
lastname: accessories
```

**The Problem**: I had put all CSV files in one folder (`raw-data/csv/`), so Athena was reading customers, products, AND addresses as one mixed table!

**The Solution**: Proper data organization. I restructured everything:
```
raw-data/csv/
├── customers/customers.csv    # Only customer data
├── products/products.csv      # Only product data  
└── addresses/addresses.csv    # Only address data
```

Then created separate Athena tables for each entity. **This was a fundamental data modeling lesson.**

**Learning**: In data lakes, folder structure = table structure. One entity type per folder!

### The Victory Moment
After reorganization, my queries finally returned clean results:
- **Customers table**: 20,000 clean customer records ✅
- **Products table**: 720,109 product records ✅
- **Addresses table**: Wait... 58,733 records instead of 30,000? 🤔

## Chapter 5: The Data Quality Detective Story

### Challenge #4: The Case of the Mysterious Address Count
My addresses.csv should have had 30,000 records, but Athena reported 58,733. Looking at the query results, I saw corrupted data:
```
addressid: Haldia_060162"
city: "Billing
state: _Shipping"
```

**Root Cause Investigation**: I downloaded the raw CSV and discovered the issue - **multi-line addresses with embedded commas and quotes**:
```csv
OR-00001,CUST-01686,"61/96,_Chauhan_Road
Haldia_060162",Haldia,West_Bengal,60162.0,Billing
```

Athena was treating each line as a separate record!

### The Data Cleaning Solution
I wrote a Python script to clean the problematic CSV:

```python
def clean_addresses_csv(input_file, output_file):
    df = pd.read_csv(input_file, quotechar='"', on_bad_lines='skip')
    
    # Clean up embedded quotes, underscores, and newlines
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].str.replace(r'["\']', '', regex=True)
            df[col] = df[col].str.replace('_', ' ')
            df[col] = df[col].str.replace('\n', ' ')
    
    df.to_csv(output_file, index=False)
```

**Results**: 
- ✅ Successfully processed and cleaned 30,000 address records
- ✅ Fixed multi-line formatting issues
- ✅ Normalized text fields
- ✅ Athena now returns correct count: 30,000

**Learning**: Real-world data is messy! Data quality issues are common and require preprocessing before analysis.

## Final Results - Mission Accomplished!

After this journey, I successfully built a complete data pipeline:

### Infrastructure Created
- **S3 Data Lake**: Organized storage for all data types
- **Glue Data Catalog**: Automated schema discovery and metadata management
- **Athena Query Engine**: SQL interface for data analysis
- **IAM Security**: Proper roles and permissions for services

### Data Successfully Ingested and Cataloged
- **Customers**: 20,000 records - demographics, contact info, registration dates
- **Products**: 720,109 records - product catalog with prices and categories  
- **Addresses**: 30,000 records - customer addresses (cleaned and normalized)
- **Inventory**: 150 JSON files - daily stock levels across 5 warehouses

### Ready for Analysis
I can now run SQL queries like:
```sql
-- Customer distribution by state
SELECT state, COUNT(*) as customer_count 
FROM retail_db.addresses 
GROUP BY state 
ORDER BY customer_count DESC;

-- Product categories analysis
SELECT category, COUNT(*) as product_count, AVG(price) as avg_price
FROM retail_db.products 
GROUP BY category;
```

## Key Learnings and Takeaways

### Technical Learnings
1. **AWS Services Integration**: S3, Glue, Athena, and IAM work together as an ecosystem
2. **Data Lake Design**: Folder structure matters - organize by entity type
3. **Service Roles**: AWS services need their own identities, separate from user permissions
4. **Data Quality**: Real data is messy and requires cleaning before analysis
5. **Schema Evolution**: Automated schema discovery is powerful but needs validation

### Process Learnings
1. **Start Simple**: Begin with basic permissions, then refine
2. **Document Everything**: Each step builds on the previous one
3. **Test Early**: Validate data quality before building complex pipelines
4. **Incremental Progress**: Tackle one challenge at a time
5. **Learn by Doing**: Hands-on experience beats theory every time

### Cost Management
- **Total AWS costs**: Under $5 for the entire project
- **S3 storage**: ~$0.10/month for 112MB of data
- **Athena queries**: A few cents per query
- **Data transfer**: Minimal within same region

## What's Next?

This foundation opens up many possibilities:
- **Advanced Analytics**: Complex joins across customer, product, and inventory data
- **Data Transformation**: ETL pipelines using AWS Glue
- **Real-time Processing**: Streaming data with Kinesis
- **Machine Learning**: Integration with SageMaker for predictive analytics
- **Visualization**: Dashboards with QuickSight
- **Automation**: Event-driven pipelines with Lambda

## Final Thoughts

This journey taught me that AWS Data Engineering is not just about learning services - it's about understanding how data flows through systems, dealing with real-world data quality issues, and building robust, scalable solutions.

The challenges I faced were typical of real projects:
- Permission configuration
- Data organization and modeling  
- Data quality issues
- Service integration complexities

But each challenge taught valuable lessons that will apply to future projects. Starting with a hands-on approach, taking it step by step, and documenting the journey made all the difference.

**For other beginners**: Don't be afraid to start! Get your hands dirty with real data, embrace the challenges, and learn from each obstacle. The AWS free tier is perfect for experimenting, and the learning experience is invaluable.

The retail data pipeline is now ready for business insights! 🚀

---

*Total project time: ~4 hours*  
*AWS services used: S3, Glue, Athena, IAM*  
*Data processed: 153 files, 112MB*  
*Records cataloged: 770,109 records across 3 main entities*  
*Status: Ready for analytics! ✅*