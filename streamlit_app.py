import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
import pickle
import requests

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def fetch_poster_from_tmdb(title):
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {'api_key': TMDB_API_KEY, 'query': title}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            poster_path = data['results'][0].get('poster_path')
            if poster_path:
                return f"{TMDB_IMAGE_BASE_URL}{poster_path}"
    return None

movies = pd.read_csv('movies.csv')
imdb_data = pd.read_csv('imdb_top_1000.csv')

with open('combined_similarity.pkl', 'rb') as f:
    combined_similarity = pickle.load(f)

imdb_data = imdb_data.rename(columns={
    'Series_Title': 'Title',
    'IMDB_Rating': 'IMDB_Rating',
    'Meta_score': 'Meta_score',
    'Genre': 'Genre',
    'Overview': 'Overview',
    'Poster_Link': 'Poster_Link'
})

imdb_data = imdb_data[imdb_data['Title'].isin(movies['Title'])]
movie_titles = movies['Title'].tolist()

def recommend_movies_with_preferences(user_preferences, combined_similarity, top_n=10):
    user_indices = [
        movies[movies['Title'] == title].index[0]
        for title in user_preferences
        if title in movies['Title'].tolist()
    ]
    if not user_indices:
        st.error("No valid movie preferences found. Please select valid movies.")
        return pd.DataFrame(columns=['Title'])
    avg_sim_scores = combined_similarity[user_indices].mean(axis=0)
    sim_scores = list(enumerate(avg_sim_scores))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    user_indices_set = set(user_indices)
    top_indices = [i[0] for i in sim_scores if i[0] not in user_indices_set][:top_n]
    recommendations = movies.iloc[top_indices][['Title']]
    return recommendations

def enrich_recommendations(recommendations):
    enriched_data = recommendations.merge(
        imdb_data[['Title', 'IMDB_Rating', 'Meta_score', 'Genre', 'Overview']],
        on='Title',
        how='left'
    )
    enriched_data['Poster_Link'] = enriched_data['Title'].apply(fetch_poster_from_tmdb)
    return enriched_data

def filter_and_sort_movies(imdb_data, genre, sort_by, top_n=50, page=1):
    if genre != "All":
        imdb_data = imdb_data[imdb_data['Genre'].str.contains(genre, case=False, na=False)]
    imdb_data = imdb_data.sort_values(by=sort_by, ascending=False)
    start_index = (page - 1) * top_n
    end_index = start_index + top_n
    total_pages = len(imdb_data) // top_n + (1 if len(imdb_data) % top_n > 0 else 0)
    return imdb_data.iloc[start_index:end_index], total_pages

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Recommendations"

def set_active_tab(tab_name):
    st.session_state.active_tab = tab_name

st.title("🎥 Movie Recommendation System")

tab1, tab2 = st.tabs(["Recommendations", "Top Movies"])

with tab1:
    set_active_tab("Recommendations")
    user_preferences = st.multiselect(
        "Select movies you liked/watched:",
        options=movie_titles,
        default=[],
    )

    if st.button("Get Recommendations", key="recommend_button"):
        if not user_preferences:
            st.error("Please select at least one movie.")
        else:
            recommendations = recommend_movies_with_preferences(user_preferences, combined_similarity)
            if recommendations.empty:
                st.error("No recommendations found. Try selecting different movies.")
            else:
                enriched_recommendations = enrich_recommendations(recommendations)
                st.write("🎬 **Movies you might like:**")
                for _, row in enriched_recommendations.iterrows():
                    poster_url = row['Poster_Link'] or "https://via.placeholder.com/150"
                    st.image(poster_url, width=150, caption=row['Title'])
                    st.markdown(f"### {row['Title']}")
                    st.write(f"**IMDb Rating:** {row['IMDB_Rating']}")
                    st.write(f"**Meta Score:** {row['Meta_score']}")
                    st.write(f"**Genre:** {row['Genre']}")
                    st.write(f"**Overview:** {row['Overview']}")
                    st.write("---")

with tab2:
    set_active_tab("Top Movies")
    st.write("🎥 **Top Movies**")
    genre = st.selectbox("Filter by genre:", ["All"] + sorted(imdb_data['Genre'].str.split(", ").explode().unique()))
    sort_by_label = st.radio("Sort by:", ["IMDb Rating", "Meta Score"], horizontal=True)
    sort_by = "IMDB_Rating" if sort_by_label == "IMDb Rating" else "Meta_score"
    top_n = st.radio("Number of movies to display:", [10, 50, 100], horizontal=True)

    if "page" not in st.session_state:
        st.session_state.page = 1

    filtered_movies, total_pages = filter_and_sort_movies(imdb_data, genre, sort_by, top_n, st.session_state.page)

    if filtered_movies.empty:
        st.write("No more results to show.")
    else:
        for _, row in filtered_movies.iterrows():
            poster_url = fetch_poster_from_tmdb(row['Title']) or "https://via.placeholder.com/150"
            st.image(poster_url, width=150, caption=row['Title'])
            st.markdown(f"### {row['Title']}")
            st.write(f"**IMDb Rating:** {row['IMDB_Rating']}")
            st.write(f"**Meta Score:** {row['Meta_score']}")
            st.write(f"**Genre:** {row['Genre']}")
            st.write(f"**Overview:** {row['Overview']}")
            st.write("---")

    def update_page(delta):
        st.session_state.page += delta

    if st.session_state.active_tab == "Top Movies":
        col1, col2, col3 = st.columns([1, 13, 1])
        with col1:
            prev_clicked = st.button("<-", on_click=update_page, args=(-1,))
        with col2:
            st.markdown(
                f"<div style='text-align: center;'><strong>Page {st.session_state.page} of {total_pages}</strong></div>",
                unsafe_allow_html=True
            )
        with col3:
            next_clicked = st.button("->", on_click=update_page, args=(1,))

    if st.session_state.page < 1:
        st.session_state.page = 1
    elif st.session_state.page > total_pages:
        st.session_state.page = total_pages
