#**🎥 Movie Recommendation System**

A web application that recommends movies based on your preferences and displays top movies with detailed information and posters fetched from TMDB. Built with Python and Streamlit.

**🚀 Features**

Personalized Recommendations: Select movies you've liked, and the app suggests similar movies.
Top Movies Browsing: Explore top-rated movies by genre, IMDb ratings, or meta scores.
Rich Information: View movie details, including genres, IMDb ratings, meta scores, and overviews.
Visual Appeal: Displays movie posters fetched from TMDB.

**📋 Prerequisites**

Python: Version 3.7 or higher
TMDB API Key: Obtain an API key from TMDB.

**🛠️ Setup Instructions**

Clone the Repository:
git clone https://github.com/your-username/movie-recommendation-system.git
cd movie-recommendation-system

Install Dependencies: Install the required Python libraries:
pip install -r requirements.txt

Set Up TMDB API Key:
Create a .env file in the root directory.
Add your TMDB API key to the .env file: (see .env.example)
TMDB_API_KEY=your_tmdb_api_key_here

Run the Application: Launch the Streamlit app with:
streamlit run app.py

**🗂️ Data Files**

movies.csv: Contains the list of movies used for recommendations.
imdb_top_1000.csv: Contains detailed information about top-rated movies.
combined_similarity.pkl: Precomputed similarity matrix for recommendations.

**📖 Usage**

1. Recommendations Tab
Select movies you've liked from the dropdown.
Click Get Recommendations to see similar movies with their details and posters.
2. Top Movies Tab
Browse top-rated movies by genre.
Sort movies by IMDb ratings or meta scores.
Adjust the number of movies displayed (10, 50, or 100).

**🌐 TMDB API Integration**

Posters are fetched using the TMDB API. Ensure you have a valid TMDB API key in the .env file.

**🛡️ License**

This project is licensed under the MIT License.
