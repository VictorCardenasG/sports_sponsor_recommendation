import csv
from pymongo import MongoClient

# MongoDB connection settings
mongo_uri = "mongodb://localhost:27017/"
mongo_db = "athlete_sponsorships"
collection_name = "athletes"

# Initialize MongoDB client and collection
client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[collection_name]

# Function to process the CSV and insert data into MongoDB
def insert_athletes_from_csv(csv_file):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            # Convert specific fields into structured lists and types
            row["Nouns"] = [noun.strip() for noun in row["Nouns"].split(",")]
            row["Values"] = [value.strip() for value in row["Values"].split(",")]
            row["Adjectives"] = [adj.strip() for adj in row["Adjectives"].split(",")]
            row["Age"] = float(row["Age"])
            row["IG Followers"] = row["IG Followers"].replace('M', '000000').replace('K', '000')  # Optionally convert IG followers to numeric
            row["Sports Sponsors"] = [sponsor.strip() for sponsor in row["Sports Sponsors"].split(",")]
            
            # Insert the record into MongoDB
            collection.insert_one(row)
        print("Data inserted successfully.")

# Run the function to insert data
csv_file = "C:/Users/Victor Cardenas/Documents/msc/semestre-3/bases_datos/vcg_proyecto_bda/data/athletes_sponsors.csv"  # Replace with your CSV file path
insert_athletes_from_csv(csv_file)

# Close MongoDB connection
client.close()
