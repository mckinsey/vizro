import random
import string
from datetime import datetime, time, timedelta

import numpy as np
import pandas as pd

# Set the random seed for reproducibility
random.seed(42)


# Function to generate random strings of 5 words
def random_words(n=5):
    return " ".join(["".join(random.choices(string.ascii_lowercase, k=5)) for _ in range(n)])


cities_coordinates = {
    "New York City, NY": {"latitude": 40.7128, "longitude": -74.0060},
    "Los Angeles, CA": {"latitude": 34.0522, "longitude": -118.2437},
    "Chicago, IL": {"latitude": 41.8781, "longitude": -87.6298},
    "Houston, TX": {"latitude": 29.7604, "longitude": -95.3698},
    "Phoenix, AZ": {"latitude": 33.4484, "longitude": -112.0740},
    "Philadelphia, PA": {"latitude": 39.9526, "longitude": -75.1652},
    "San Antonio, TX": {"latitude": 29.4241, "longitude": -98.4936},
    "San Diego, CA": {"latitude": 32.7157, "longitude": -117.1611},
    "Dallas, TX": {"latitude": 32.7767, "longitude": -96.7970},
    "San Jose, CA": {"latitude": 37.3382, "longitude": -121.8863},
    "Austin, TX": {"latitude": 30.2672, "longitude": -97.7431},
    "Jacksonville, FL": {"latitude": 30.3322, "longitude": -81.6557},
    "Fort Worth, TX": {"latitude": 32.7555, "longitude": -97.3308},
    "Columbus, OH": {"latitude": 39.9612, "longitude": -82.9988},
    "Indianapolis, IN": {"latitude": 39.7684, "longitude": -86.1581},
    "Charlotte, NC": {"latitude": 35.2271, "longitude": -80.8431},
    "San Francisco, CA": {"latitude": 37.7749, "longitude": -122.4194},
    "Seattle, WA": {"latitude": 47.6062, "longitude": -122.3321},
    "Denver, CO": {"latitude": 39.7392, "longitude": -104.9903},
    "Washington, DC": {"latitude": 38.9072, "longitude": -77.0369},
    "Boston, MA": {"latitude": 42.3601, "longitude": -71.0589},
    "El Paso, TX": {"latitude": 31.7619, "longitude": -106.4850},
    "Nashville, TN": {"latitude": 36.1627, "longitude": -86.7816},
    "Detroit, MI": {"latitude": 42.3314, "longitude": -83.0458},
    "Portland, OR": {"latitude": 45.5152, "longitude": -122.6784},
    "Boise, ID": {"latitude": 43.6150, "longitude": -116.2023},
    "Las Vegas, NV": {"latitude": 36.1699, "longitude": -115.1398},
    "Louisville, KY": {"latitude": 38.2527, "longitude": -85.7585},
    "Milwaukee, WI": {"latitude": 43.0389, "longitude": -87.9065},
    "Albuquerque, NM": {"latitude": 35.0844, "longitude": -106.6504},
    "Tucson, AZ": {"latitude": 32.2226, "longitude": -110.9747},
    "Fresno, CA": {"latitude": 36.7378, "longitude": -119.7871},
    "Sacramento, CA": {"latitude": 38.5816, "longitude": -121.4944},
    "Kansas City, MO": {"latitude": 39.0997, "longitude": -94.5786},
    "Mesa, AZ": {"latitude": 33.4152, "longitude": -111.8315},
    "Atlanta, GA": {"latitude": 33.7490, "longitude": -84.3880},
    "Omaha, NE": {"latitude": 41.2565, "longitude": -95.9345},
    "Raleigh, NC": {"latitude": 35.7796, "longitude": -78.6382},
    "Miami, FL": {"latitude": 25.7617, "longitude": -80.1918},
    "Tulsa, OK": {"latitude": 36.1540, "longitude": -95.9928},
    "Minneapolis, MN": {"latitude": 44.9778, "longitude": -93.2650},
    "Wichita, KS": {"latitude": 37.6872, "longitude": -97.3301},
    "New Orleans, LA": {"latitude": 29.9511, "longitude": -90.0715},
    "Arlington, TX": {"latitude": 32.7357, "longitude": -97.1081},
    "Cleveland, OH": {"latitude": 41.4993, "longitude": -81.6944},
    "Tampa, FL": {"latitude": 27.9506, "longitude": -82.4572},
    "Bakersfield, CA": {"latitude": 35.3733, "longitude": -119.0187},
    "Aurora, CO": {"latitude": 39.7294, "longitude": -104.8319},
    "Anaheim, CA": {"latitude": 33.8366, "longitude": -117.9143},
    "Honolulu, HI": {"latitude": 21.3069, "longitude": -157.8583},
    "Santa Ana, CA": {"latitude": 33.7455, "longitude": -117.8677},
    "St. Louis, MO": {"latitude": 38.6270, "longitude": -90.1994},
    "Riverside, CA": {"latitude": 33.9806, "longitude": -117.3755},
    "Corpus Christi, TX": {"latitude": 27.8006, "longitude": -97.3964},
    "Lexington, KY": {"latitude": 38.0406, "longitude": -84.5037},
    "Stockton, CA": {"latitude": 37.9577, "longitude": -121.2908},
    "Henderson, NV": {"latitude": 36.0395, "longitude": -114.9817},
    "Pittsburgh, PA": {"latitude": 40.4406, "longitude": -79.9959},
    "Anchorage, AK": {"latitude": 61.2181, "longitude": -149.9003},
    "Cincinnati, OH": {"latitude": 39.1031, "longitude": -84.5120},
    "St. Paul, MN": {"latitude": 44.9537, "longitude": -93.0900},
    "Greensboro, NC": {"latitude": 36.0726, "longitude": -79.7920},
    "Lincoln, NE": {"latitude": 40.8136, "longitude": -96.7026},
    "Buffalo, NY": {"latitude": 42.8864, "longitude": -78.8784},
    "Plano, TX": {"latitude": 33.0198, "longitude": -96.6989},
    "Orlando, FL": {"latitude": 28.5383, "longitude": -81.3792},
    "St. Petersburg, FL": {"latitude": 27.7676, "longitude": -82.6403},
    "Chandler, AZ": {"latitude": 33.3062, "longitude": -111.8413},
    "Toledo, OH": {"latitude": 41.6528, "longitude": -83.5379},
    "Irvine, CA": {"latitude": 33.6846, "longitude": -117.8265},
    "Reno, NV": {"latitude": 39.5296, "longitude": -119.8138},
    "Lubbock, TX": {"latitude": 33.5779, "longitude": -101.8552},
    "Madison, WI": {"latitude": 43.0731, "longitude": -89.4012},
    "Chesapeake, VA": {"latitude": 36.7682, "longitude": -76.2875},
}


def random_city_lat(city):
    return cities_coordinates["latitude"]


def random_city_long(city):
    return cities_coordinates["longitude"]


def get_random_city_data(cities_coordinates, num_rows):
    """Parses the given dictionary of cities and their lat/long coordinates
    and returns a dictionary with random cities and their corresponding lat/long values.

    Parameters:
        cities_coordinates (dict): Dictionary with city names as keys and lat/long as values.
        num_rows (int): Number of random rows (cities) to select.

    Returns:
        dict: A dictionary with keys 'city', 'latitude', and 'longitude', where values are lists.
    """
    # Randomly select cities
    cities = list(cities_coordinates.keys())

    # random_cities = np.random.choice(cities, num_rows)
    # Extract latitude and longitude
    latitudes = []
    longitudes = []
    random_cities = []
    for row in range(num_rows):
        random_city = random.choice(cities)

        random_cities.append(random_city)
        latitudes.append(cities_coordinates[random_city]["latitude"])
        longitudes.append(cities_coordinates[random_city]["longitude"])

    return {"city": list(random_cities), "latitude": latitudes, "longitude": longitudes}


# Function to generate a random date between two dates
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


# Create the dataframe
num_rows = 350  # Number of rows in the dataframe

# Date range from 1st January 2025 to 1st December 2025
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 1)

city_data = get_random_city_data(cities_coordinates, num_rows)


def random_time():
    hour = random.randint(8, 17)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return time(hour, minute, second)


df = pd.DataFrame(
    {
        # 6 columns with integers from 1 to 5
        "col1": np.random.randint(1, 6, num_rows),
        "col2": np.random.randint(1, 6, num_rows),
        "col3": np.random.randint(1, 6, num_rows),
        "col4": np.random.randint(1, 6, num_rows),
        "col5": np.random.randint(1, 6, num_rows),
        "col6": np.random.randint(1, 6, num_rows),
        # 3 columns with boolean values
        "boolean_col1": np.random.choice([True, False], num_rows),
        "boolean_col2": np.random.choice([True, False], num_rows),
        "boolean_col3": np.random.choice([True, False], num_rows),
        # 2 columns with strings "positive", "neutral", "negative"
        "sentiment_col1": np.random.choice(["positive", "neutral", "negative"], num_rows),
        "sentiment_col2": np.random.choice(["positive", "neutral", "negative"], num_rows),
        # 2 columns with 5 randomly generated words
        "random_words_col1": [random_words() for _ in range(num_rows)],
        "random_words_col2": [random_words() for _ in range(num_rows)],
        # 1 column with integer IDs from 1 to 20
        "id_col": np.random.randint(1000, 1024, num_rows),
        # 1 column with integer IS from 1 to 500
        "is_col": np.random.randint(1, 234, num_rows),
        # Random date between 1st Jan 2025 and 1st Dec 2025
        "random_date": [random_date(start_date, end_date) for _ in range(num_rows)],
        # Random time between 8am and 17pm
        "random_time": [random_time() for _ in range(num_rows)],
        # Random city data
        "city": city_data["city"],
        "latitude": city_data["latitude"],
        "longitude": city_data["longitude"],
    }
)

df = df.rename(
    columns={
        "col1": "Empathy",
        "col2": "Professionalism",
        "col3": "Kindness",
        "col4": "Effective Communication",
        "col5": "Active Listening",
        "col6": "Customization",
        "boolean_col1": "Concern Addressed",
        "boolean_col2": "Upsale Attempted",
        "boolean_col3": "Upsale Success",
        "sentiment_col1": "Client Tone",
        "sentiment_col2": "Agent Tone",
        "random_words_col1": "Topic",
        "random_words_col2": "Summary",
        "id_col": "Agent ID",
        "is_col": "Caller ID",
        "random_date": "Call Date",
        "random_time": "Time",
        "city": "Caller City",
        "latitude": "latitude",
        "longitude": "longitude",
    }
)
data = pd.DataFrame(df)


df.to_excel("output.xlsx", index=False)
