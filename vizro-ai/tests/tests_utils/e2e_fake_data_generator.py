import pandas as pd
import random

# List of music genres
music_genres = [
    "Pop", "Rock", "Hip-Hop", "Jazz", "Classical", "Electronic",
    "Reggae", "Country", "Blues", "R&B", "Metal", "Folk"
]

# List of countries
countries = [
    "United States", "Canada", "United Kingdom", "Germany", "France",
    "Japan", "Australia", "Brazil", "India", "South Korea", "Italy", "Spain"
]


# Function to generate fake music genre popularity dataset
def create_genre_popularity_by_country(start_year=1980, end_year=2023, records_per_year=10):
    data = []

    # Generate data for each year
    for year in range(start_year, end_year + 1):
        for _ in range(records_per_year):
            genre = random.choice(music_genres)
            country = random.choice(countries)
            popularity_score = round(random.uniform(0, 100), 2)  # Popularity score between 0 and 100

            data.append({
                "Year": year,
                "Country": country,
                "Genre": genre,
                "Popularity Score": popularity_score
            })

    return pd.DataFrame(data)
