from flask import Flask, render_template, request
from sdb_sponsor_recommendation import SponsorRecommender

app = Flask(__name__)

# Initialize your recommender class here
recommender = SponsorRecommender(mongo_uri="mongodb://localhost:27017/",
                                 mongo_db="athlete_sponsorships",
                                 collection_name="sponsor_identity",
                                 athlete_collection="athletes",
                                 w2v_model_path = "C:/Users/Victor Cardenas/Documents/msc/semestre-3/bases_datos/python/word2vec/GoogleNews-vectors-negative300.bin")

@app.route('/')
def home():
    return render_template('index.html')  # Render the main HTML page

@app.route('/recommend', methods=['POST'])
def recommend():
    # Get input from form
    nouns = request.form.get('nouns').split(',')
    adjectives = request.form.get('adjectives').split(',')
    values = request.form.get('values').split(',')
    nationality = request.form.get('nationality')
    target_audience = request.form.get('target_audience')

    # Get recommendations
    recommendations = recommender.recommend_sponsors(
        nouns, adjectives, values, nationality, target_audience)

    return render_template('results.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
