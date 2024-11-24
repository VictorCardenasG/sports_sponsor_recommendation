from cassandra.cluster import Cluster

# Connect to Cassandra
cluster = Cluster(['127.0.0.1'])
session = cluster.connect('athletes_ks')

# Fetch all athlete names
rows = session.execute("SELECT athlete_name FROM athletes")

# Update each athlete's record
for row in rows:
    athlete_name = row.athlete_name
    athlete_name_lower = athlete_name.lower()
    session.execute(
        "UPDATE athletes SET athlete_name_lower = %s WHERE athlete_name = %s",
        (athlete_name_lower, athlete_name)
    )

print("Updated all athlete names to lowercase.")
