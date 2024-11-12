from pymongo import MongoClient

# Connect to the MongoDB client
mongo_uri = "mongodb://localhost:27017/"
client = MongoClient(mongo_uri)
db = client["athlete_sponsorships"]
collection = db["sponsor_identity"]

# Find both entries
nike_entry = collection.find_one({"Sponsor": "Nike"})
nike_quote_entry = collection.find_one({"Sponsor": '"Nike'})

if nike_quote_entry:
    # Merge fields of `'"Nike'` into `'Nike'`
    # Assuming the fields Nouns, Values, Adjectives, Nationalities, and Target Audiences contain lists
    fields_to_merge = ["Nouns", "Values", "Adjectives", "Nationalities", "Target Audiences"]

    for field in fields_to_merge:
        if field in nike_quote_entry:
            # If field exists in both entries, combine them; else, add the field
            if field in nike_entry:
                nike_entry[field] = list(set(nike_entry[field] + nike_quote_entry[field]))
            else:
                nike_entry[field] = nike_quote_entry[field]
    
    # Update the 'Nike' entry with the merged data
    collection.update_one({"Sponsor": "Nike"}, {"$set": nike_entry})

    # Delete the '"Nike' entry
    collection.delete_one({"Sponsor": '"Nike'})
    print("Merged Nike' data into Nike and deleted Nike' entry.")
else:
    print("No entry found for Nike'. Nothing to merge.")

# Close the MongoDB client
client.close()