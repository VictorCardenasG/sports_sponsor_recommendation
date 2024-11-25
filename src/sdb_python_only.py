# Original dictionary with sponsors and slogans
sponsors_dict = {
    'Yonex': 'Japanese craftsmanship and innovation.',
    'Salomon': 'Shaping the future of Sport since 1947',
    'Hoka One One': 'Empowering everyone to feel like they can fly. A bold and unexpected approach to performance footwear. It\'s Time To Fly',
    'La Sportiva': 'Climbing, Mountain Running, Mountaineering, Skialp',
    'Les Trailiers': 'Your local Les Schwab carries recreational towing trailer tires to handle any tow load, effectively dissipate heat, and minimize fishtailing.',
    'Compressport': 'HIGH-END COMPRESSION GARMENTS Join the COMPRESSPORT Community !',
    'Billabong': 'KnowTheFeeling',
    'Rip Curl': 'The Ultimate Surfing Company',
    'Roxy': 'Inspired by the mountain and the wave, weve been empowering women since 1990.',
    "O'Neill": 'FirstNameInTheWater',
    'Quiksilver': 'Premium marine and powersports parts, accessories, and engine care products.',
    'Surftech': 'WHERE LEGENDS ARE MADE Iconic designs, meticulously replicated and paired with cutting edge technology.',
    '-1': 'slogan goes here',
    'Fanatics': 'sports is my passion',
    'TaylorMade': 'The Official Instagram of TaylorMade Golf - Carlsbad, CA',
    'Uniqlo': 'The global official Instagram #UNIQLO #LifeWear',
    'Mercedes-Benz': 'Love of invention will never end. Carl Benz Fueling innovation with every drive',
    'Ralph Lauren': 'Defining timeless style since 1967',
    'Red Bull': 'watch the World Of Red Bull',
    'Li Ning': 'Chinas premier sports brand. Named for and founded by, world class gymnast, Mr. Li Ning. Established in 1990.',
    'Skechers USA': 'Comfort, Fashion & Innovation',
    'Wilson Sporting Goods': 'Empowering every human to live like an athlete.',
    'Peak Sports': 'Leading Sports company with global network',
    'New Era': 'Founded in 1920 in Buffalo, NY A global brand of sport, culture, style, & self-expression',
    'Callaway Golf': 'WE FIT THE GAME Innovative - Performance-Driven - Authentic',
    'Franklin Sports': 'We bring sports to life for athletes of all ages. Official Batting Glove of Major League Baseball.',
    'Monster Energy': 'Unleash the Beast! MonsterEnergy',
    'Nissan Motor': 'Innovation for excitement.',
    'Porsche Automobil Holding': 'Your daily dose of Porsche. By our community, for our community.',
    'Audi': 'Innovating the road ahead Be part of progress VorsprungDurchTechnik',
    'Converse': 'Est 1908','Lululemon': ' Movement, mindfulness, community and more.', 'Athleta': ' Women moving women, forward.', 'Prana': ' Keep Pushing Boundaries ', 'SFX Sports': 'slogan goes here', 'Nike': 'Just do it.', '2XU': 'Creating a fitter, healthier world', 'Adidas': 'Impossible is Nothing', 'Li-Ning': ' Make the change', 'Yoga Alliance': 'More Yoga Better World', 'Patagonia': ' Were in business to save our home planet', 'Shimano': 'Closer to Nature, Closer to People', 'Under Armour': ' Under Armour Makes You Better', 'Cricket Australia': 'Attitude is everything', 'Fox Sports': ' Fans for Life', 'Mizuno': ' Reach Beyond', 'Head': ' Performance is a HEAD game', 'Everlast': ' The Choice of Champions Since 1910', 'Wilson': ' The joy of sport. The gift of game', 'Asics': ' Sound Mind, Sound Body', 'New Balance': ' We Got Now', 'Lacoste': ' Life is a Beautiful Sport', 'Brooks': 'Lets Run There', 'Saucony': ' Run for Good', 'Cliff Keen': ' Train like a Champion', 'Puma': ' FOREVER. FASTER', 'Fila': ' One World, One FILA', 'Diadora': 'Normalize High Mileage', 'Bianchi': ' The color of legends and dreams', 'Reebok': ' Because life is not a spectator sport', 'Gymshark': ' United We Sweat', 'Dunlop': ' The love of the game.'
}

# Remove invalid entries (e.g., '-1': 'slogan goes here')
valid_sponsors_dict = {key: value for key, value in sponsors_dict.items() if key != '-1' and value != 'slogan goes here'}

# Convert the dictionary into the format required for MongoDB insertion
sponsor_documents = [{"Sponsor": sponsor, "Slogan": slogan} for sponsor, slogan in valid_sponsors_dict.items()]

# Print the final format ready for MongoDB insertion
print(sponsor_documents)

# Assuming you're using PyMongo
import pymongo

# Connect to MongoDB and access your database and collection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["athlete_sponsorships"]
sponsor_identity_collection = db["sponsor_identity"]

try:
    for sponsor, slogan in valid_sponsors_dict.items():
        sponsor_identity_collection.update_many(
            {"Sponsor": sponsor},  # filter based on Sponsor name
            {"$set": {"Slogan": slogan}},  # update the Slogan field
            upsert=True  # insert if not found
        )

    print("Data inserted successfully")
except Exception as e:
    print("Error during insertion:", e)