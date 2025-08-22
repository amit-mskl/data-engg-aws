# Databricks Concepts - Hands-On Tutorial

**Level:** Basic | **Duration:** 4 hours | **Participants:** 1.8K

## Overview
Learn about the power of Databricks Lakehouse and help you scale up your data engineering and machine learning skills.

## Learning Objectives
By the end of this tutorial, you will be able to:
- Understand core Databricks architectural concepts
- Work with Delta Lake and its features
- Implement data pipelines using Databricks
- Understand Unity Catalog and data governance
- Apply MLflow for machine learning lifecycle management
- Work with structured streaming

## Prerequisites
- Completion of "Introduction to Databricks" tutorial
- Basic knowledge of SQL and Python
- Understanding of data engineering concepts
- Access to Databricks workspace

## Module 1: Databricks Architecture Deep Dive (45 minutes)

### The Lakehouse Architecture
The Databricks Lakehouse combines the best features of data lakes and data warehouses.

#### Key Components:
- **Control Plane**: Manages the Databricks environment
- **Data Plane**: Where your data and compute resources reside
- **Unity Catalog**: Centralized governance and security
- **Delta Lake**: Storage layer with ACID transactions

### Hands-On Exercise 1: Understanding the Architecture
```python
# Check your current workspace configuration
print("Workspace Information:")
print(f"Workspace URL: {spark.conf.get('spark.databricks.workspaceUrl', 'Not available')}")
print(f"Cluster Name: {spark.conf.get('spark.databricks.clusterUsageTags.clusterName', 'Not available')}")
print(f"Runtime Version: {spark.conf.get('spark.databricks.clusterUsageTags.sparkVersion', 'Not available')}")
```

### Multi-layer Architecture
```python
# Explore the different layers
%fs ls /databricks-datasets/
%fs ls /mnt/
%fs ls /tmp/
```

## Module 2: Delta Lake Fundamentals (60 minutes)

### What is Delta Lake?
Delta Lake is an open-source storage layer that brings ACID transactions to Apache Spark and big data workloads.

#### Key Features:
- **ACID Transactions**: Ensures data consistency
- **Schema Enforcement**: Prevents bad data from corrupting tables
- **Time Travel**: Query historical versions of data
- **Schema Evolution**: Modify table schema over time

### Hands-On Exercise 2: Creating Your First Delta Table
```python
# Create sample data
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from delta.tables import *
import datetime

# Sample sales data
sales_data = [
    (1, "2023-01-01", "Product A", 100, 10.0),
    (2, "2023-01-01", "Product B", 150, 15.0),
    (3, "2023-01-02", "Product A", 200, 10.0),
    (4, "2023-01-02", "Product C", 75, 25.0),
    (5, "2023-01-03", "Product B", 300, 15.0)
]

columns = ["transaction_id", "date", "product", "quantity", "price"]
df = spark.createDataFrame(sales_data, columns)

# Write as Delta table
df.write.format("delta").mode("overwrite").saveAsTable("sales_data")
```

### Working with Delta Tables
```python
# Read Delta table
sales_delta = spark.read.format("delta").table("sales_data")
sales_delta.show()

# Get table information
%sql
DESCRIBE EXTENDED sales_data
```

### Time Travel Feature
```python
# Add more data
new_sales = [
    (6, "2023-01-04", "Product A", 120, 10.0),
    (7, "2023-01-04", "Product D", 90, 30.0)
]

new_df = spark.createDataFrame(new_sales, columns)
new_df.write.format("delta").mode("append").saveAsTable("sales_data")

# Check current data
print("Current version:")
spark.read.format("delta").table("sales_data").count()
```

```sql
-- Time travel queries
SELECT * FROM sales_data VERSION AS OF 0;
SELECT * FROM sales_data TIMESTAMP AS OF '2023-12-01 00:00:00';

-- Show table history
DESCRIBE HISTORY sales_data;
```

### Schema Evolution and Enforcement
```python
# Try to insert data with wrong schema (this should fail)
try:
    wrong_schema_data = [(8, "2023-01-05", "Product E", "invalid_quantity", 20.0)]
    wrong_df = spark.createDataFrame(wrong_schema_data, columns)
    wrong_df.write.format("delta").mode("append").saveAsTable("sales_data")
except Exception as e:
    print(f"Schema enforcement prevented bad data: {e}")
```

```python
# Schema evolution - adding a new column
from pyspark.sql.types import *

# Add a new column with schema evolution
sales_with_category = spark.read.table("sales_data").withColumn("category", lit("Electronics"))
sales_with_category.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable("sales_data")

# Verify the schema change
spark.read.table("sales_data").printSchema()
```

## Module 3: Advanced Delta Lake Operations (45 minutes)

### MERGE Operations (Upserts)
```python
# Create updates and new records
updates_data = [
    (1, "2023-01-01", "Product A", 110, 10.0, "Electronics"),  # Update existing
    (8, "2023-01-05", "Product E", 50, 35.0, "Home")  # New record
]

updates_df = spark.createDataFrame(updates_data, ["transaction_id", "date", "product", "quantity", "price", "category"])

# Perform MERGE operation
delta_table = DeltaTable.forName(spark, "sales_data")

delta_table.alias("target").merge(
    updates_df.alias("updates"),
    "target.transaction_id = updates.transaction_id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

# Verify the merge
spark.read.table("sales_data").orderBy("transaction_id").show()
```

### DELETE Operations
```sql
-- Delete specific records
DELETE FROM sales_data WHERE product = 'Product C';

-- Verify deletion
SELECT * FROM sales_data ORDER BY transaction_id;
```

### VACUUM Operations
```python
# Check table size before vacuum
%sql
DESCRIBE DETAIL sales_data

# Vacuum old files (be careful in production!)
%sql
VACUUM sales_data RETAIN 0 HOURS -- Only for demo, use longer retention in production

# Show how vacuum affects storage
%sql
DESCRIBE DETAIL sales_data
```

## Module 4: Data Pipelines and ETL (60 minutes)

### Building Data Pipelines
Data pipelines in Databricks can be built using notebooks, jobs, and Delta Live Tables.

### Hands-On Exercise 3: Simple ETL Pipeline
```python
# Extract: Read from multiple sources
# Simulating different data sources
customers_data = [
    (1, "Alice Johnson", "alice@email.com", "New York"),
    (2, "Bob Smith", "bob@email.com", "California"),
    (3, "Charlie Brown", "charlie@email.com", "Texas")
]

orders_data = [
    (101, 1, "2023-01-01", 100.0),
    (102, 2, "2023-01-02", 150.0),
    (103, 1, "2023-01-03", 200.0),
    (104, 3, "2023-01-04", 75.0)
]

# Create DataFrames
customers_df = spark.createDataFrame(customers_data, ["customer_id", "name", "email", "state"])
orders_df = spark.createDataFrame(orders_data, ["order_id", "customer_id", "order_date", "amount"])

# Save as Delta tables
customers_df.write.format("delta").mode("overwrite").saveAsTable("customers")
orders_df.write.format("delta").mode("overwrite").saveAsTable("orders")
```

```python
# Transform: Create analytical views
# Customer order summary
customer_summary = spark.sql("""
    SELECT 
        c.customer_id,
        c.name,
        c.state,
        COUNT(o.order_id) as total_orders,
        SUM(o.amount) as total_spent,
        AVG(o.amount) as avg_order_value,
        MAX(o.order_date) as last_order_date
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name, c.state
""")

# Load: Save transformed data
customer_summary.write.format("delta").mode("overwrite").saveAsTable("customer_analytics")
customer_summary.show()
```

### Data Quality Checks
```python
# Implement data quality checks
def data_quality_check(df, table_name):
    print(f"Data Quality Report for {table_name}:")
    print(f"Total records: {df.count()}")
    print(f"Null values per column:")
    
    # Check for nulls in each column
    for column in df.columns:
        null_count = df.filter(col(column).isNull()).count()
        print(f"  {column}: {null_count} nulls")
    
    # Check for duplicates
    total_records = df.count()
    distinct_records = df.distinct().count()
    print(f"Duplicate records: {total_records - distinct_records}")
    print("-" * 40)

# Run quality checks
data_quality_check(spark.read.table("customers"), "customers")
data_quality_check(spark.read.table("orders"), "orders")
```

## Module 5: Structured Streaming Concepts (45 minutes)

### Introduction to Structured Streaming
Structured Streaming is a scalable and fault-tolerant stream processing engine built on Spark SQL.

### Hands-On Exercise 4: Basic Streaming Example
```python
# Simulate streaming data
import time
from pyspark.sql.functions import current_timestamp

# Create a streaming source (simulated)
# In real scenarios, you'd connect to Kafka, Kinesis, etc.
streaming_data = spark.readStream.format("rate").option("rowsPerSecond", 2).load()

# Add some transformations
processed_stream = streaming_data.select(
    col("timestamp"),
    col("value"),
    (col("value") % 10).alias("category"),
    current_timestamp().alias("processed_time")
)

# Write to console for demo
query = processed_stream.writeStream \
    .outputMode("append") \
    .format("console") \
    .trigger(processingTime="10 seconds") \
    .start()

# Let it run for a bit then stop
time.sleep(30)
query.stop()
```

### Streaming Aggregations
```python
# Window-based aggregations
windowed_counts = streaming_data.groupBy(
    window(col("timestamp"), "30 seconds", "10 seconds"),
    (col("value") % 5).alias("group")
).count()

# This would be used in a real streaming scenario
print("Streaming aggregation query defined")
```

## Module 6: Unity Catalog and Data Governance (30 minutes)

### Understanding Unity Catalog
Unity Catalog provides centralized access control, auditing, lineage, and data discovery across Databricks workspaces.

### Key Concepts:
- **Metastore**: Top-level container for metadata
- **Catalog**: Grouping of databases/schemas
- **Schema**: Container for tables, views, functions
- **Tables/Views**: Data objects

### Hands-On Exercise 5: Working with Catalogs
```sql
-- List available catalogs
SHOW CATALOGS;

-- List schemas in current catalog
SHOW SCHEMAS;

-- List tables in current schema
SHOW TABLES;
```

```python
# Working with three-level namespace
# catalog.schema.table format
spark.sql("CREATE SCHEMA IF NOT EXISTS tutorial_catalog.tutorial_schema")

# Move our tables to the new schema
spark.sql("""
    CREATE TABLE IF NOT EXISTS tutorial_catalog.tutorial_schema.managed_sales
    AS SELECT * FROM sales_data
""")
```

### Data Lineage and Audit
```sql
-- Check table information including lineage
DESCRIBE EXTENDED tutorial_catalog.tutorial_schema.managed_sales;

-- Show table history for audit purposes
DESCRIBE HISTORY tutorial_catalog.tutorial_schema.managed_sales;
```

## Module 7: MLflow Integration (45 minutes)

### MLflow Components:
- **MLflow Tracking**: Record and query experiments
- **MLflow Models**: Package ML models
- **MLflow Model Registry**: Central model store

### Hands-On Exercise 6: Basic MLflow Experiment
```python
import mlflow
import mlflow.sklearn
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import pandas as pd

# Prepare sample data for ML
sales_pandas = spark.read.table("sales_data").toPandas()

# Simple feature engineering
sales_pandas['price_quantity'] = sales_pandas['price'] * sales_pandas['quantity']
sales_pandas = pd.get_dummies(sales_pandas, columns=['product'])

# Prepare features and target
feature_columns = [col for col in sales_pandas.columns if col not in ['transaction_id', 'date', 'quantity', 'category']]
X = sales_pandas[feature_columns]
y = sales_pandas['quantity']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# MLflow experiment
with mlflow.start_run():
    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Make predictions
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    
    # Log parameters and metrics
    mlflow.log_param("model_type", "LinearRegression")
    mlflow.log_metric("mse", mse)
    
    # Log model
    mlflow.sklearn.log_model(model, "linear_regression_model")
    
    print(f"Model MSE: {mse}")
```

### Model Registry
```python
# Register the model
model_name = "sales_prediction_model"

# This would typically be done through the UI or with model registry API
print(f"Model {model_name} would be registered in MLflow Model Registry")
```

## Module 8: Performance Optimization (30 minutes)

### Optimization Techniques:
- **Partitioning**: Organize data for faster queries
- **Z-Order**: Optimize file layout for better performance
- **Caching**: Keep frequently accessed data in memory
- **Broadcast Joins**: Optimize small table joins

### Hands-On Exercise 7: Performance Optimization
```python
# Partitioning example
large_dataset = spark.range(1000000).withColumn("category", col("id") % 10)

# Write with partitioning
large_dataset.write \
    .format("delta") \
    .partitionBy("category") \
    .mode("overwrite") \
    .saveAsTable("partitioned_data")

# Z-Order optimization
%sql
OPTIMIZE partitioned_data ZORDER BY (id);
```

```python
# Caching for repeated access
frequently_used_data = spark.read.table("customer_analytics")
frequently_used_data.cache()

# Use the cached data multiple times
print("Count:", frequently_used_data.count())
print("Avg spent:", frequently_used_data.agg(avg("total_spent")).collect()[0][0])
```

## Practical Exercises

### Exercise 1: Complete ETL Pipeline
1. Create a medallion architecture (Bronze, Silver, Gold layers)
2. Implement data quality checks at each layer
3. Use Delta Lake features for data versioning

### Exercise 2: Streaming Analytics
1. Set up a streaming source
2. Implement real-time aggregations
3. Write results to Delta tables

### Exercise 3: ML Workflow
1. Create an end-to-end ML pipeline
2. Use MLflow for experiment tracking
3. Register and version your models

### Exercise 4: Data Governance
1. Set up proper schema organization
2. Implement access controls
3. Document data lineage

## Best Practices
- **Data Organization**: Use consistent naming conventions
- **Schema Management**: Plan schema evolution carefully
- **Performance**: Partition large tables appropriately
- **Security**: Implement proper access controls
- **Monitoring**: Set up alerts and monitoring
- **Documentation**: Document your data assets

## Troubleshooting Common Issues
1. **Schema Evolution Conflicts**: Use explicit schema management
2. **Performance Issues**: Check partition strategy and query patterns
3. **Memory Issues**: Optimize cluster configuration and data caching
4. **Concurrent Write Conflicts**: Implement proper error handling

## Next Steps
After completing this tutorial:
1. Explore Advanced Delta Lake features
2. Learn about Delta Live Tables
3. Implement production-grade data pipelines
4. Study advanced MLflow features
5. Explore Databricks security features

## Assessment Questions
1. Explain the key differences between a traditional data warehouse and a Lakehouse
2. What are the ACID properties that Delta Lake provides?
3. How does time travel work in Delta Lake?
4. What is the purpose of Unity Catalog?
5. Describe the components of MLflow
6. When would you use MERGE vs INSERT in Delta Lake?
7. What are the benefits of partitioning in Delta tables?
8. How does structured streaming handle fault tolerance?

## Resources
- [Delta Lake Documentation](https://docs.delta.io/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Unity Catalog Guide](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Structured Streaming Guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [Databricks Performance Tuning](https://docs.databricks.com/optimizations/index.html)

---
*This tutorial provides a comprehensive overview of core Databricks concepts. Practice with real datasets and scenarios to deepen your understanding.*