from pymongo import MongoClient
from collections import defaultdict, Counter

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["athlete_sponsorships"]
athletes_collection = db["athletes"]
sponsor_identity_collection = db["sponsor_identity"]

# Clear any existing data
sponsor_identity_collection.drop()

# Step 1: Tally total mentions across all athletes
total_trait_counts = {
    "Nouns": Counter(),
    "Values": Counter(),
    "Adjectives": Counter(),
    "Nationalities": Counter(),
    "Target Audiences": Counter()
}

# Accumulate the total counts
for athlete in athletes_collection.find():
    total_trait_counts["Nouns"].update(athlete.get("Nouns", []))
    total_trait_counts["Values"].update(athlete.get("Values", []))
    total_trait_counts["Adjectives"].update(athlete.get("Adjectives", []))
    total_trait_counts["Nationalities"].update([athlete.get("Nationality", "Unknown")])
    total_trait_counts["Target Audiences"].update([athlete.get("Core Audience", "Unknown")])

# Step 2: Collect and weight traits for each sponsor
sponsor_data = defaultdict(lambda: {
    "Nouns": Counter(),
    "Values": Counter(),
    "Adjectives": Counter(),
    "Nationalities": Counter(),
    "Target Audiences": Counter()
})

for athlete in athletes_collection.find():
    sponsors = athlete.get("Sports Sponsors", [])
    for sponsor in sponsors:
        sponsor_data[sponsor]["Nouns"].update(athlete.get("Nouns", []))
        sponsor_data[sponsor]["Values"].update(athlete.get("Values", []))
        sponsor_data[sponsor]["Adjectives"].update(athlete.get("Adjectives", []))
        sponsor_data[sponsor]["Nationalities"].update([athlete.get("Nationality", "Unknown")])
        sponsor_data[sponsor]["Target Audiences"].update([athlete.get("Core Audience", "Unknown")])

# Step 3: Insert each sponsor's data into the sponsor_identity collection with weighted values
for sponsor, traits in sponsor_data.items():
    sponsor_document = {"Sponsor": sponsor, "Slogan": ""}  # Add slogan here if available

    # Calculate weighted traits for each category
    for trait_type in ["Nouns", "Values", "Adjectives", "Nationalities", "Target Audiences"]:
        weighted_traits = []
        for trait, count in traits[trait_type].items():
            # Calculate the weight for this trait for this sponsor
            total_mentions = total_trait_counts[trait_type][trait]
            if total_mentions > 0:
                weight = (count / total_mentions) + 1
                weighted_traits.append((trait, weight))
        
        # Add the weighted traits to the document
        sponsor_document[trait_type] = weighted_traits

    # Insert the sponsor document into MongoDB
    sponsor_identity_collection.insert_one(sponsor_document)

print("Sponsor identity collection created successfully!")
client.close()
