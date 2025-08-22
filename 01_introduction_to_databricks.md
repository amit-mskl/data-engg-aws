# Introduction to Databricks - Hands-On Tutorial

**Level:** Basic | **Duration:** 3 hours | **Participants:** 4.9K

## Overview
Learn about the Databricks Lakehouse platform and how it can modernize data architectures and improve data management processes.

## Learning Objectives
By the end of this tutorial, you will be able to:
- Understand what Databricks is and its core value proposition
- Navigate the Databricks workspace
- Create and manage clusters
- Work with notebooks and basic operations
- Understand the Lakehouse architecture

## Prerequisites
- Basic understanding of cloud computing concepts
- Familiarity with data concepts (databases, files, etc.)
- Access to Databricks workspace (Community Edition or trial)

## Module 1: What is Databricks? (30 minutes)

### Introduction to Databricks
Databricks is a unified analytics platform that combines data engineering, data science, and machine learning on a single platform built on Apache Spark.

### Key Features
- **Unified Platform**: Single platform for all data workloads
- **Collaborative Environment**: Real-time collaboration on notebooks
- **Auto-scaling Clusters**: Automatic resource management
- **Built-in Security**: Enterprise-grade security features
- **Multi-cloud Support**: Available on AWS, Azure, and GCP

### The Lakehouse Architecture
The Lakehouse combines the best of data warehouses and data lakes:
- **Data Lake**: Store all types of data (structured, semi-structured, unstructured)
- **Data Warehouse**: ACID transactions, schema enforcement, governance
- **Machine Learning**: Native ML capabilities and MLflow integration

## Module 2: Databricks Workspace Tour (45 minutes)

### Accessing Databricks
1. Navigate to your Databricks workspace URL
2. Log in with your credentials
3. Explore the main interface

### Workspace Components
- **Sidebar Navigation**: Access to notebooks, clusters, jobs, etc.
- **Workspace**: File system for organizing notebooks and folders
- **Data**: Browse databases, tables, and files
- **Compute**: Manage clusters and compute resources
- **Jobs**: Schedule and monitor automated workflows
- **ML**: Machine learning experiments and models

### Hands-On Exercise 1: Workspace Navigation
1. Create a new folder in your workspace called "Tutorial"
2. Navigate through different sections of the sidebar
3. Explore the Data section to see available databases

## Module 3: Creating and Managing Clusters (45 minutes)

### Understanding Clusters
Clusters are groups of virtual machines that provide the compute power for your Databricks workloads.

### Cluster Types
- **All-Purpose Clusters**: Interactive workloads, notebook development
- **Job Clusters**: Automated jobs, terminated after job completion

### Hands-On Exercise 2: Create Your First Cluster
1. Navigate to the Compute section
2. Click "Create Cluster"
3. Configure cluster settings:
   ```
   Cluster Name: tutorial-cluster
   Databricks Runtime: Latest LTS version
   Node Type: Smallest available option
   Workers: 1-2 nodes (for learning)
   ```
4. Click "Create Cluster" and wait for it to start

### Cluster Management Best Practices
- Use auto-termination to control costs
- Choose appropriate node types for your workload
- Monitor cluster utilization
- Use cluster policies for governance

## Module 4: Working with Notebooks (60 minutes)

### Creating Your First Notebook
1. In the Workspace, create a new notebook
2. Name it "My First Databricks Notebook"
3. Choose Python as the default language
4. Attach it to your cluster

### Notebook Basics
- **Cells**: Code blocks that can be executed
- **Magic Commands**: Special commands starting with %
- **Multiple Languages**: Python, Scala, SQL, R in the same notebook

### Hands-On Exercise 3: Basic Notebook Operations

#### Cell 1: Welcome Message
```python
print("Welcome to Databricks!")
print(f"Cluster: {spark.conf.get('spark.databricks.clusterUsageTags.clusterName')}")
```

#### Cell 2: Exploring Spark Context
```python
# Check Spark version and configuration
print(f"Spark Version: {spark.version}")
print(f"Number of cores: {sc.defaultParallelism}")
```

#### Cell 3: Working with Data
```python
# Create a simple dataset
data = [(1, "Alice", 25), (2, "Bob", 30), (3, "Charlie", 35)]
columns = ["id", "name", "age"]

# Create DataFrame
df = spark.createDataFrame(data, columns)
df.show()
```

#### Cell 4: Basic Data Operations
```python
# DataFrame operations
print("Total records:", df.count())
print("Schema:")
df.printSchema()

# Filter data
adults = df.filter(df.age >= 30)
adults.show()
```

### Magic Commands Exercise
```python
# Cell 5: Using SQL magic command
%sql
CREATE OR REPLACE TEMPORARY VIEW people AS
SELECT * FROM VALUES (1, "Alice", 25), (2, "Bob", 30), (3, "Charlie", 35) AS people(id, name, age)
```

```sql
-- Cell 6: Pure SQL cell
SELECT name, age FROM people WHERE age > 25
```

## Module 5: File System and Data Access (30 minutes)

### Databricks File System (DBFS)
DBFS is a distributed file system that allows you to access files as if they were on a local file system.

### Hands-On Exercise 4: Working with Files
```python
# List files in DBFS
%fs ls /databricks-datasets/

# Look at sample datasets
%fs ls /databricks-datasets/samples/

# Read a sample file
sample_data = spark.read.text("/databricks-datasets/README.md")
sample_data.show(5, truncate=False)
```

### Uploading Data
1. Use the Data UI to upload files
2. Access uploaded files via DBFS
3. Create tables from uploaded data

## Module 6: Basic Data Analysis Example (30 minutes)

### Hands-On Exercise 5: Analyzing Sample Data
```python
# Load the NYC taxi dataset sample
taxi_data = spark.read.parquet("/databricks-datasets/nyctaxi/tables/nyctaxi_yellow")

# Explore the data
print("Records:", taxi_data.count())
taxi_data.printSchema()
taxi_data.show(5)
```

```python
# Basic analysis
from pyspark.sql.functions import avg, max, min, count

# Calculate statistics
stats = taxi_data.agg(
    avg("fare_amount").alias("avg_fare"),
    max("fare_amount").alias("max_fare"),
    min("fare_amount").alias("min_fare"),
    count("*").alias("total_trips")
)
stats.show()
```

```python
# Group by passenger count
passenger_analysis = taxi_data.groupBy("passenger_count").agg(
    count("*").alias("trip_count"),
    avg("fare_amount").alias("avg_fare")
).orderBy("passenger_count")

passenger_analysis.show()
```

## Practical Exercises

### Exercise 1: Data Exploration
1. Load a dataset from `/databricks-datasets/`
2. Explore its schema and basic statistics
3. Create visualizations using Databricks' built-in plotting

### Exercise 2: Simple ETL
1. Create a sample dataset
2. Apply transformations (filter, group, aggregate)
3. Save the results to DBFS

### Exercise 3: Cluster Management
1. Monitor your cluster's resource usage
2. Practice starting and stopping clusters
3. Experiment with different cluster configurations

## Best Practices
- Always attach notebooks to appropriate clusters
- Use descriptive names for notebooks and folders
- Comment your code for collaboration
- Save work frequently
- Use version control for production code
- Monitor cluster costs and usage

## Next Steps
After completing this tutorial, you should:
1. Practice creating and managing different types of clusters
2. Explore more advanced notebook features
3. Try working with larger datasets
4. Learn about Databricks' security features
5. Explore the Databricks documentation and community resources

## Resources
- [Databricks Documentation](https://docs.databricks.com/)
- [Databricks Community Forums](https://community.databricks.com/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Databricks Academy](https://academy.databricks.com/)

## Quiz Questions
1. What are the main components of the Lakehouse architecture?
2. What's the difference between All-Purpose and Job clusters?
3. How do you switch between different languages in a notebook?
4. What is DBFS and how do you access files stored in it?
5. Name three benefits of using Databricks over traditional data platforms.

---
*This tutorial is designed to give you a solid foundation in Databricks basics. Take your time with each module and don't hesitate to experiment with the examples provided.*