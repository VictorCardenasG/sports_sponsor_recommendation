import csv
from collections import Counter
from cassandra.cluster import Cluster

# Path to the CSV file inside
csv_path = r"C:\Users\Victor Cardenas\Documents\msc\semestre-3\bases_datos\vcg_proyecto_bda\data\athletes_sponsors.csv"

# Step 1: Read and process the 'Values' column
value_counts = Counter()
with open(csv_path, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Split the 'Values' column into individual items and count
        values = row['Values'].split(',')
        value_counts.update(value.strip() for value in values)

# Step 2: Connect to Cassandra
cluster = Cluster(['127.0.0.1'])  
session = cluster.connect('athletes_ks')

# Step 3: Insert data into the `values_count` table
for value, count in value_counts.items():
    session.execute(
        """
        INSERT INTO values_count (value, count) VALUES (%s, %s)
        """,
        (value, count)
    )

print("Values count inserted into the table successfully.")

