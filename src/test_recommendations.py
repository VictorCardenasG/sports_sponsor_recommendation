import mongomock
import pytest
from sdb_sponsor_recommendation import SponsorRecommender  # Replace with your actual module name

@pytest.fixture
def mock_db():
    # Create a mock MongoDB client and database
    client = mongomock.MongoClient()
    db = client["athlete_sponsorships"]
    collection = db["sponsor_identity"]
    
    # Seed with sample data
    collection.insert_many([
        {
            "Sponsor": "Nike",
            "Nouns": ["athlete", "sport"],
            "Values": ["dedication", "perseverance"],
            "Adjectives": ["inspiring", "motivated"],
            "Nationalities": ["American"],
            "Target Audiences": ["youth"]
        },
        {
            "Sponsor": 'Adidas',
            "Nouns": ["champion", "athlete"],
            "Values": ["excellence"],
            "Adjectives": ["strong"],
            "Nationalities": ["American"],
            "Target Audiences": ["young athletes"]
        }
    ])
    return collection

def test_calculate_similarity_score(mock_db):
    # Initialize SponsorRecommender with the mocked database
    sponsor_recommender = SponsorRecommender(
        mongo_uri="mongodb://localhost",  # Use a valid URI for mongomock
        mongo_db="athlete_sponsorships",
        collection_name="sponsor_identity",
        w2v_model_path = "C:/Users/Victor Cardenas/Documents/msc/semestre-3/bases_datos/python/word2vec/GoogleNews-vectors-negative300.bin"
        athlete_collection=mock_db  # Pass the mocked collection here
    )
    
    # Mock word2vec similarity scores for testing
    sponsor_recommender.word2vec_model = {
        "athlete": {"athlete": 1.0, "champion": 0.8},
        "champion": {"athlete": 0.8, "champion": 1.0}
    }
    
    input_nouns = ["athlete", "champion"]
    sponsor_nouns = [("athlete", 1.5), ("champion", 1.2)]
    
    score, _ = sponsor_recommender.calculate_similarity_score(input_nouns, sponsor_nouns)
    assert score > 0  # Ensure score is positive and calculated

def test_recommend_sponsors(mock_db):
    # Initialize SponsorRecommender with the mocked database
    sponsor_recommender = SponsorRecommender(
        mongo_uri="mongodb://localhost:27017/",  # This should be acceptable for mongomock
        mongo_db="athlete_sponsorships",
        collection_name="sponsor_identity",
        w2v_model_path = "C:/Users/Victor Cardenas/Documents/msc/semestre-3/bases_datos/python/word2vec/GoogleNews-vectors-negative300.bin"
        athlete_collection=mock_db  # Pass the mocked collection here
    )
    
    # Mock inputs
    input_nouns = ["athlete", "champion"]
    input_adjectives = ["motivated", "strong"]
    input_values = ["dedication", "excellence"]
    input_nationality = "American"
    input_target_audience = "youth"
    
    top_sponsors = sponsor_recommender.recommend_sponsors(
        input_nouns, input_adjectives, input_values, input_nationality, input_target_audience
    )
    
    assert len(top_sponsors) > 0  # Should recommend at least one sponsor
    assert "Nike" in [sponsor["Sponsor"] for sponsor in top_sponsors]  # Expect "Nike" in the top sponsors
