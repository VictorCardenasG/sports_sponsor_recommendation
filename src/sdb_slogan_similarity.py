from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['athlete_sponsorships']
collection = db['sponsor_identity']

class SloganRecommender:

    def __init__(self, mongo_uri, mongo_db, collection_name, athlete_collection):
        print("Initializing Sponsor Recommender...")

        # Initialize MongoDB client and load Word2Vec model
        self.client = MongoClient(mongo_uri)
        self.db = self.client[mongo_db]
        self.sponsor_collection = self.db[collection_name]
        if isinstance(athlete_collection, str):
            self.athlete_collection = self.db[athlete_collection]
        else:
            self.athlete_collection = athlete_collection

    def find_most_similar_slogans(self, user_input):
        try:
            results = collection.find(
                {"$text": {"$search": user_input}},
                {"Sponsor": 1, "score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})])

            seen_sponsors = set()
            deduplicated_results = []

            for result in results:
                if result["Sponsor"] not in seen_sponsors:
                    deduplicated_results.append(result)
                    seen_sponsors.add(result["Sponsor"])

                if len(deduplicated_results) >= 3:  # Limit to top 3
                    break

            return deduplicated_results

        except ConnectionFailure:
            print("Failed to connect to MongoDB")
            return []


# # Example usage
# user_input = "motivation inspiration performance"
# results = find_most_similar_slogans(user_input)
# for result in results:
#     print(f"Sponsor: {result['Sponsor']}, Score: {round(result['score'],2)}")


