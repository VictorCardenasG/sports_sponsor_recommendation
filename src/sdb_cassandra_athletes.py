import pandas as pd
from cassandra.cluster import Cluster

# Connect to Cassandra
cluster = Cluster(['127.0.0.1'])  
session = cluster.connect()

# Set the keyspace
session.set_keyspace('athletes_ks')  

# Create the table 
session.execute("""
CREATE TABLE IF NOT EXISTS athletes (
    athlete_name TEXT PRIMARY KEY,
    nouns SET<TEXT>,
    values SET<TEXT>,
    adjectives SET<TEXT>,
    sponsor TEXT,
    ig_followers TEXT,
    practiced_sport TEXT,
    nationality TEXT,
    core_audience TEXT,
    net_worth TEXT,
    age INT,
    agent TEXT,
    sports_sponsors LIST<TEXT>
);
""")

# Load the CSV file
csv_file = r"C:\Users\Victor Cardenas\Documents\msc\semestre-3\bases_datos\vcg_proyecto_bda\data\athletes_sponsors.csv" 
df = pd.read_csv(csv_file)

# Clean and preprocess data
def preprocess_value(value):
    if pd.isna(value):
        return None
    return value.strip().lower()

# Insert rows into Cassandra
for _, row in df.iterrows():
    session.execute("""
    INSERT INTO athletes (athlete_name, nouns, values, adjectives, sponsor, ig_followers, 
                          practiced_sport, nationality, core_audience, net_worth, age, 
                          agent, sports_sponsors)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row['Athlete Name'].strip().lower(),  # Case-insensitive athlete name
        set(map(preprocess_value, row['Nouns'].split(','))) if pd.notna(row['Nouns']) else None,
        set(map(preprocess_value, row['Values'].split(','))) if pd.notna(row['Values']) else None,
        set(map(preprocess_value, row['Adjectives'].split(','))) if pd.notna(row['Adjectives']) else None,
        preprocess_value(row['Sponsor']),
        preprocess_value(row['IG Followers']),
        preprocess_value(row['Practiced Sport']),
        preprocess_value(row['Nationality']),
        preprocess_value(row['Core Audience']),
        preprocess_value(row['Net Worth (Estimated)']),
        int(row['Age']) if pd.notna(row['Age']) else None,
        preprocess_value(row['Agent']),
        row['Sports Sponsors'].split(',') if pd.notna(row['Sports Sponsors']) else None
    ))

print("Data inserted successfully!")
