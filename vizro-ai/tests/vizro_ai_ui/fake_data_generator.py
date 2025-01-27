import numpy as np
import pandas as pd

# List of music genres
music_genres = [
    "Pop",
    "Rock",
    "Hip-Hop",
    "Jazz",
    "Classical",
    "Electronic",
    "Reggae",
    "Country",
    "Blues",
    "R&B",
    "Metal",
    "Folk",
]

# List of countries
countries = [
    "United States",
    "Canada",
    "United Kingdom",
    "Germany",
    "France",
    "Japan",
    "Australia",
    "Brazil",
    "India",
    "South Korea",
    "Italy",
    "Spain",
]


# Function to generate fake music genre popularity dataset
def create_genre_popularity_by_country(first_year=1980, last_year=2023):
    return pd.DataFrame(
        {
            "Year": (np.arange(first_year, last_year)),
            "Countries": np.random.choice(countries, size=last_year - first_year),
            "Genre": np.random.choice(music_genres, size=last_year - first_year),
            "Popularity Score": np.random.choice(np.arange(0, 100), size=last_year - first_year),
        }
    )
