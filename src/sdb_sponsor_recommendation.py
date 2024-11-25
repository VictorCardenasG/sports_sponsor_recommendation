
from pymongo import MongoClient
from gensim.models import KeyedVectors

class SponsorRecommender:

    def __init__(self, mongo_uri, mongo_db, collection_name, athlete_collection, w2v_model_path):
        print("Initializing Sponsor Recommender...")

        # Initialize MongoDB client and load Word2Vec model
        self.client = MongoClient(mongo_uri)
        self.db = self.client[mongo_db]
        self.sponsor_collection = self.db[collection_name]
        if isinstance(athlete_collection, str):
            self.athlete_collection = self.db[athlete_collection]
        else:
            self.athlete_collection = athlete_collection
        
        print("Loading Word2Vec model...")
        self.word2vec_model = KeyedVectors.load_word2vec_format(w2v_model_path, binary=True)
        print("Word2Vec model loaded successfully.")

    def close(self):
        print("Closing database connection.")
        self.client.close()

    def calculate_similarity_score(self, user_words, sponsor_words):
        total_score = 0.0
        top_matches = []
        matched_words = set()
        for user_word in user_words:
            max_similarity = 0.0
            best_match = None
            for sponsor_word, weight in sponsor_words:
                if user_word in self.word2vec_model and sponsor_word in self.word2vec_model and sponsor_word not in matched_words:
                    # Check if word2vec_model is a mock dictionary or an actual Word2Vec model
                    if isinstance(self.word2vec_model, dict):
                        # Use dictionary lookup for mock model
                        similarity = self.word2vec_model[user_word].get(sponsor_word, 0)
                    else:
                        # Use similarity method for Word2Vec model
                        similarity = self.word2vec_model.similarity(user_word, sponsor_word)
                    
                    weighted_similarity = similarity * weight
                    if weighted_similarity > max_similarity:
                        max_similarity = weighted_similarity
                        best_match = sponsor_word
                        matched_words.add(sponsor_word)
            if best_match:
                top_matches.append((user_word, best_match, max_similarity))
            total_score += max_similarity

        return total_score, top_matches

    def calculate_similarity_athlete(self, user_words, sponsor_words):
        total_score = 0.0
        top_matches = []
        matched_words = set()
        for user_word in user_words:
            max_similarity = 0.0
            best_match = None
            for sponsor_word in sponsor_words:
                if user_word in self.word2vec_model and sponsor_word in self.word2vec_model and sponsor_word not in matched_words:
                    # Check if word2vec_model is a mock dictionary or an actual Word2Vec model
                    if isinstance(self.word2vec_model, dict):
                        # Use dictionary lookup for mock model
                        similarity = self.word2vec_model[user_word].get(sponsor_word, 0)
                    else:
                        # Use similarity method for Word2Vec model
                        similarity = self.word2vec_model.similarity(user_word, sponsor_word)
                    
                    
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_match = sponsor_word
                        matched_words.add(sponsor_word)
            if best_match:
                top_matches.append((user_word, best_match, max_similarity))
            total_score += max_similarity

        return total_score, top_matches

    def get_similar_athletes_2(self, sponsor_name):
        # Retrieve athletes with the specified sponsor
        athletes = list(self.athlete_collection.find({"Sports Sponsors": sponsor_name}, {"Athlete Name": 1}))
        return [athlete["Athlete Name"] for athlete in athletes]

    def get_similar_athletes(self, sponsor_name, input_nouns, input_adjectives, input_values, input_nationality, input_target_audience):
        # Retrieve athletes sponsored by the given sponsor
        athletes = list(self.athlete_collection.find({"Sports Sponsors": sponsor_name}))

        athlete_scores = []
        athletes_reviewed = set()

        # Iterate over each athlete and calculate similarity
        for athlete in athletes:
            athlete_name = athlete["Athlete Name"]
            if athlete_name in athletes_reviewed:
                continue
            else:
                athletes_reviewed.add(athlete_name)
            athlete_nouns = athlete.get("Nouns", [])
            athlete_adjectives = athlete.get("Adjectives", [])
            athlete_values = athlete.get("Values", [])
            athlete_nationality = athlete.get("Nationality", "")
            athlete_target_audience = athlete.get("Core Audience", "")

            # Calculate similarity scores for each attribute
            score, _ = self.calculate_similarity_athlete(input_nouns, athlete_nouns)
            score += self.calculate_similarity_athlete(input_adjectives, athlete_adjectives)[0]
            score += self.calculate_similarity_athlete(input_values, athlete_values)[0]
            score += self.calculate_similarity_athlete([input_nationality], [athlete_nationality])[0]
            score += self.calculate_similarity_athlete([input_target_audience], [athlete_target_audience])[0]

            # Store the score and athlete name
            athlete_scores.append((athlete_name, score))

        # Sort athletes by similarity score in descending order
        athlete_scores.sort(key=lambda x: x[1], reverse=True)

        # Return top 3 athletes
        top_athletes = [athlete for athlete, _ in athlete_scores[:3]]
        return top_athletes



    def recommend_sponsors(self, input_nouns, input_adjectives, input_values, input_nationality, input_target_audience):
        recommendations = {}
        top_word_matches = {}

        print("Fetching sponsor data from the database...")
        sponsor_data = self.sponsor_collection.find()
        print("Sponsor data fetched. Processing each sponsor...")
        sponsors_reviewed = set()
        for idx, sponsor in enumerate(sponsor_data, start=1):

            sponsor_name = sponsor["Sponsor"]
            
            # Skip sponsors with name '-1' or empty string
            if sponsor_name == "-1" or not sponsor_name:
                print(f"Skipping sponsor {idx}: {sponsor_name} (invalid name)")
                continue
            if sponsor_name in sponsors_reviewed:
                continue
            else:
                sponsors_reviewed.add(sponsor_name)

            print(f"Processing sponsor {idx}: {sponsor_name}")
            sponsor_chemistry = 0.0

            # Calculate scores and top words for each attribute
            score, nouns_matches = self.calculate_similarity_score(input_nouns, sponsor.get("Nouns", []))
            sponsor_chemistry += score
            score, adjectives_matches = self.calculate_similarity_score(input_adjectives, sponsor.get("Adjectives", []))
            sponsor_chemistry += score
            score, values_matches = self.calculate_similarity_score(input_values, sponsor.get("Values", []))
            sponsor_chemistry += score
            score, nationality_matches = self.calculate_similarity_score([input_nationality], sponsor.get("Nationalities", []))
            sponsor_chemistry += score
            score, audience_matches = self.calculate_similarity_score([input_target_audience], sponsor.get("Target Audiences", []))
            sponsor_chemistry += score

            # Store results
            recommendations[sponsor_name] = sponsor_chemistry
            top_word_matches[sponsor_name] = {
                "Nouns": nouns_matches,
                "Adjectives": adjectives_matches,
                "Values": values_matches,
                "Nationality": nationality_matches,
                "Target Audience": audience_matches
            }

            print(f"Total score for {sponsor_name}: {sponsor_chemistry:.2f}")

        print("Sorting sponsors by scores to get the top recommendations...")
        top_sponsors = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:3]
        print("Recommendation process complete.\n")

        results = []
        for sponsor_name, score in top_sponsors:
            # Retrieve similar athletes for each top sponsor
            similar_athletes = self.get_similar_athletes(sponsor_name, input_nouns, input_adjectives, input_values, input_nationality, input_target_audience)
            results.append({
                "Sponsor": sponsor_name,
                "Score": score,
                "Top Matches": top_word_matches[sponsor_name],
                "Similar Athletes": similar_athletes[:3]
            })

        return results




# Example usage
if __name__ == "__main__":
    mongo_uri = "mongodb://localhost:27017/"
    mongo_db = "athlete_sponsorships"
    sponsor_collection = "sponsor_identity"
    athlete_collection = "athletes"
    w2v_model_path = "C:/Users/Victor Cardenas/Documents/msc/semestre-3/bases_datos/python/word2vec/GoogleNews-vectors-negative300.bin"

    recommender = SponsorRecommender(mongo_uri, mongo_db, sponsor_collection, athlete_collection, w2v_model_path)

    try:
        # Simulated user input
        nouns = ["Soccer","Striker","Icon"]
        adjectives = ["Power","Endurance","Resilience"]
        values = ["Dominant","Inspirational","Ferocious"]
        nationality = "italian"
        target_audience = "men"

        print("Starting sponsor recommendation process...")
        recommendations = recommender.recommend_sponsors(nouns, adjectives, values, nationality, target_audience)

        print("\nTop 3 Sponsor Recommendations:")
        for rec in recommendations:
            print(f"Sponsor: {rec['Sponsor']}, Score: {rec['Score']:.2f}")
            print("Top Matches:")
            for category, matches in rec["Top Matches"].items():
                top_words = ", ".join([f"User input: {user_word} with DB entry: {word} ({similarity:.2f})" for user_word, word, similarity in matches])
                print(f"  {category}: {top_words}")
            print("Similar Athletes Sponsored:")
            print(", ".join(rec["Similar Athletes"]) if rec["Similar Athletes"] else "None found")
            print("\n" + "-"*40 + "\n")

    finally:
        recommender.close()

