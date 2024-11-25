from flask import Flask, render_template, request, jsonify
from cassandra.cluster import Cluster
from sdb_sponsor_recommendation import SponsorRecommender
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

app = Flask(__name__)



# SloganRecommender class (same as you provided)
class SloganRecommender:

    def __init__(self, mongo_uri, mongo_db, collection_name, athlete_collection):
        print("Initializing Sponsor Recommender...")
        self.client = MongoClient(mongo_uri)
        self.db = self.client[mongo_db]
        self.sponsor_collection = self.db[collection_name]
        if isinstance(athlete_collection, str):
            self.athlete_collection = self.db[athlete_collection]
        else:
            self.athlete_collection = athlete_collection

    def find_most_similar_slogans(self, user_input):
        try:
            results = self.sponsor_collection.find(
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

# Initialize SloganRecommender
slogan_recommender = SloganRecommender(
    mongo_uri="mongodb://localhost:27017/",
    mongo_db="athlete_sponsorships",
    collection_name="sponsor_identity",
    athlete_collection="athletes"
)

@app.route('/explore-data/slogan-similarity', methods=['GET', 'POST'])
def slogan_similarity():
    if request.method == 'POST':
        user_input = request.form['words']
        results = slogan_recommender.find_most_similar_slogans(user_input)

        # Pass results to the template for display
        return render_template('slogan_results.html', results=results)
    
    return render_template('slogan_similarity.html')  # GET request, show the form

# MongoDB initialization for sponsor recommendation
recommender = SponsorRecommender(mongo_uri="mongodb://localhost:27017/",
                                 mongo_db="athlete_sponsorships",
                                 collection_name="sponsor_identity",
                                 athlete_collection="athletes",
                                 w2v_model_path="C:/Users/Victor Cardenas/Documents/msc/semestre-3/bases_datos/python/word2vec/GoogleNews-vectors-negative300.bin")

# Cassandra initialization
cassandra_cluster = Cluster(['127.0.0.1'])
cassandra_session = cassandra_cluster.connect()
cassandra_session.set_keyspace('athletes_ks')  # Use your keyspace name here

# Function to search athlete (case-insensitive)
def search_athlete(athlete_name):
    athlete_name = athlete_name.strip().lower()  # Convert to lowercase
    query = "SELECT * FROM athletes WHERE athlete_name = %s"
    row = cassandra_session.execute(query, [athlete_name]).one()
    if row:
        return row
    else:
        return "Athlete not found!"

# Function to search athletes by name for autocomplete 
def search_athletes_by_name(query):
    query = f"%{query.lower()}%"  
    rows = cassandra_session.execute("SELECT athlete_name FROM athletes WHERE athlete_name LIKE %s LIMIT 10", (query,))
    return [row.athlete_name for row in rows]

@app.route('/')
def home():
    return render_template('index.html')  # Render the main HTML page

@app.route('/explore_data')
def explore_data():
    return render_template('explore_data.html')

# @app.route('/recommend', methods=['POST'])
# def recommend():
#     # Get input from form
#     nouns = request.form.get('nouns').split(',')
#     adjectives = request.form.get('adjectives').split(',')
#     values = request.form.get('values').split(',')
#     nationality = request.form.get('nationality')
#     target_audience = request.form.get('target_audience')

#     # Get recommendations from MongoDB
#     recommendations = recommender.recommend_sponsors(
#         nouns, adjectives, values, nationality, target_audience)

#     return render_template('results.html', recommendations=recommendations)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    # Get input from form
    nouns = request.form.get('nouns', '').split(',')
    adjectives = request.form.get('adjectives', '').split(',')
    values = request.form.get('values', '').split(',')
    nationality = request.form.get('nationality', '')
    target_audience = request.form.get('target_audience', '')

    # Get recommendations from MongoDB
    recommendations = recommender.recommend_sponsors(
        nouns, adjectives, values, nationality, target_audience)

    return render_template('results.html', recommendations=recommendations)


@app.route('/recommend_sponsors', methods=['POST'])
def recommend_sponsors():
    if request.method == 'POST':
        try:
            # Debugging logs
            print("Form submission received!")
            print("Request form data:", request.form)
            
            # Retrieve form data
            nouns = request.form['nouns'].split(',')
            adjectives = request.form['adjectives'].split(',')
            values = request.form['values'].split(',')
            nationality = request.form['nationality']
            target_audience = request.form['target_audience']
            
            # Debugging logs
            print("Parsed form values:")
            print("Nouns:", nouns)
            print("Adjectives:", adjectives)
            print("Values:", values)
            print("Nationality:", nationality)
            print("Target Audience:", target_audience)

            # Call recommender logic
            recommendations = recommender.recommend_sponsors(
                nouns, adjectives, values, nationality, target_audience
            )
            
            print("Recommendations generated:", recommendations)

            # Render results
            return render_template('recommendation_results.html', recommendations=recommendations)

        except Exception as e:
            # Debugging logs for errors
            print("Error processing the form:", str(e))
            return "An error occurred. Check the logs.", 500
        
@app.route('/sponsor_recommendation')
def sponsor_recommendation():
    # Renders the page where the user can input details for the sponsor recommendation
    return render_template('sponsor_recommendation_form.html')

# @app.route('/results', methods=['POST'])
# def recommend():
#     # Get input from form
#     nouns = request.form.get('nouns').split(',')
#     adjectives = request.form.get('adjectives').split(',')
#     values = request.form.get('values').split(',')
#     nationality = request.form.get('nationality')
#     target_audience = request.form.get('target_audience')

#     # Get recommendations from MongoDB
#     recommendations = recommender.recommend_sponsors(
#         nouns, adjectives, values, nationality, target_audience)

#     # Render the results page with recommendations
#     return render_template('results.html', recommendations=recommendations)



@app.route('/explore-data/athlete-search', methods=['GET', 'POST'])
def athlete_search():
    if request.method == 'POST':
        athlete_name = request.form.get('athlete_name')  # Get user input for athlete name
        result = search_athlete(athlete_name)  # Call the search function
        return render_template('athlete_search_result.html', result=result)
    return render_template('athlete_search.html')

@app.route('/autocomplete-athlete', methods=['GET'])
def autocomplete_athlete():
    query = request.args.get('query', '').strip().lower()  # Ensure the query is in lowercase
    select_query = "SELECT athlete_name_lower FROM athletes WHERE athlete_name_lower LIKE %s"
    rows = cassandra_session.execute(select_query, [f"%{query}%"])

    # Fetch the matching results and prepare the response
    suggestions = [row.athlete_name_lower for row in rows]
    return jsonify({'suggestions': suggestions})


@app.route('/values-popularity', methods=['GET', 'POST'])
def values_popularity():
    if request.method == 'POST':
        user_input = request.form.get('value') 
        query = "SELECT count FROM values_count WHERE value = %s"
        rows = cassandra_session.execute(query, [user_input])
        
        # Check if the value exists and fetch count
        count = rows.one()
        if count:
            count_result = count.count
        else:
            count_result = 0  # If value does not exist, return 0
        
        return render_template('values_popularity.html', count=count_result, value=user_input)
    return render_template('values_popularity.html', count=None)


if __name__ == '__main__':
    app.run(debug=True)
