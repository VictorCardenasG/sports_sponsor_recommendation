from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['athlete_sponsorships']  # Replace with your database name
collection = db['sponsor_identity']

# Retrieve all sponsors
sponsors = collection.find({}, {"Sponsor": 1, "_id": 0})

# Convert the result to a list
sponsor_list = [sponsor["Sponsor"] for sponsor in sponsors]

print(len(sponsor_list))
print(sponsor_list[31:65])
# Create the dictionary
sponsor_dict = {sponsor: 'slogan goes here' for sponsor in sponsor_list if sponsor}

# Print the dictionary
print(sponsor_dict)