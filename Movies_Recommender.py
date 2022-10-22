import streamlit as st
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import requests
import random


def app():
    # ==========================Fetching Posters through the TMDB API======================================#
    def fetch_poster(movie_id):

        url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(
            movie_id)
        data = requests.get(url)
        # Checking if the server is fulfilling the request
        # status code 200 --> Successful OK!
        # status code 304 --> Response had invalid or missing data

        if data.status_code != 304:
            # Parsing the response(data) to dictionary
            poster_path = data.json()['poster_path']
        else:
            poster_path = None

        if poster_path is None:
            full_path = "https://image.shutterstock.com/z/stock-vector-unavailable-silver-shiny-emblem-scales" \
                        "-pattern-vector-illustration-detailed-1676250781.jpg"
        else:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path

        return full_path

    # ========================================Function to recommend movies======================================#
    @st.cache(allow_output_mutation=True)
    def recommend(movie, technique):
        movie_name = []
        movie_posters = []
        links = []

        a1 = np.array(content_latent_matrix.loc[movie]).reshape(1, -1)
        a2 = np.array(collaborative_latent_matrix.loc[movie]).reshape(1, -1)

        # Calculating the similarity of this movie with the others in the list
        score1 = cosine_similarity(content_latent_matrix, a1).reshape(-1)
        score2 = cosine_similarity(collaborative_latent_matrix, a2).reshape(-1)

        if technique == 'Content-Based':
            content = sorted(enumerate(score1.tolist()), reverse=True, key=lambda x: x[1])
            for i in content[0:50]:
                movie_id = final.iloc[i[0]].movieId
                links.append("https://www.themoviedb.org/movie/{}".format(movie_id))
                movie_posters.append(fetch_poster(movie_id))
                movie_name.append(final.iloc[i[0]].title)
            return links, movie_name, movie_posters

        elif technique == 'Collaborative-Based':
            collaborative = sorted(enumerate(score2.tolist()), reverse=True, key=lambda x: x[1])
            for i in collaborative[0:50]:
                movie_id = final.iloc[i[0]].movieId
                links.append("https://www.themoviedb.org/movie/{}".format(movie_id))
                movie_posters.append(fetch_poster(movie_id))
                movie_name.append(final.iloc[i[0]].title)
            return links, movie_name, movie_posters

        elif technique == 'Hybrid-Based (Recommended)':
            # an average measure of both content and collaborative
            hybrid = sorted(enumerate(((score1 + score2) / 2.0).tolist()), reverse=True, key=lambda x: x[1])
            for i in hybrid[0:50]:
                movie_id = final.iloc[i[0]].movieId
                links.append("https://www.themoviedb.org/movie/{}".format(movie_id))
                movie_posters.append(fetch_poster(movie_id))
                movie_name.append(final.iloc[i[0]].title)
            return links, movie_name, movie_posters

    # ==============================================Loading Data======================================================#
    final = pickle.load(open('MovieRecommender/Final.pkl', 'rb'))
    content_latent_matrix = pickle.load(open('MovieRecommender/content_latent_matrix.pkl', 'rb'))
    collaborative_latent_matrix = pickle.load(open('MovieRecommender/collaborative_latent_matrix.pkl', 'rb'))
    movie_list = pickle.load(open('MovieRecommender/movie_list.pkl', 'rb'))

    # ===========================================App Layout & Integration==========================================#
    def set_bg():
        """
        A function to unpack an image from url and set as bg.
        Returns
        -------
        The background.
        """
        st.markdown(
            f"""
             <style>
             .css-ocqkz7{{
                 backdrop-filter: blur(2px);
             }} 
             .stApp {{
                 background: url("https://repository-images.githubusercontent.com/275336521/20d38e00-6634-11eb-9d1f-6a5232d0f84f");
                 background-size: cover;
             }} 
             </style>
             """,
            unsafe_allow_html=True
        )

    # ===============================================================================================================#
    set_bg()
    movie_emojis = ["🍿", "🎥", "🎞", "🎬", "📺", "📽"]
    st.title("{}Movie Recommender System".format(random.choice(movie_emojis)))

    selected_movie = st.selectbox(
        "Select a movie from the dropdown below,",
        movie_list,
        index=6396)
    feat = ['Content-Based', 'Collaborative-Based', 'Hybrid-Based (Recommended)']
    features = st.sidebar.radio('Select the filtering method,', feat, index=feat.index('Hybrid-Based (Recommended)'))

    # ====================================Recommending 10 Similar Movies=======================================#
    # ====================================Checking & creating the session state================================#
    st.subheader("Top 10 Similar Movies Curated For You...")
    movies_per_page = 10
    if 'previous_movie' not in st.session_state:
        st.session_state['previous_movie'] = selected_movie
    current_movie = selected_movie
    if current_movie != st.session_state['previous_movie']:
        if 'rounds_i' in st.session_state:
            st.session_state['rounds_i'] = 0
        st.session_state['previous_movie'] = current_movie

    if 'rounds_i' not in st.session_state:
        st.session_state['rounds_i'] = 0

    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)
        links, recommended_movie_names, recommended_movie_posters = recommend(selected_movie, features)

        if st.button("Get More Movies"):
            if st.session_state['rounds_i'] <= len(links):
                st.session_state['rounds_i'] += movies_per_page

    current_links = links[st.session_state['rounds_i']:st.session_state['rounds_i'] + movies_per_page]
    current_names = recommended_movie_names[st.session_state['rounds_i']:st.session_state['rounds_i'] + movies_per_page]
    current_posters = recommended_movie_posters[
                      st.session_state['rounds_i']:st.session_state['rounds_i'] + movies_per_page]

    if st.session_state['rounds_i'] < len(links):

        for i in range(len(current_links)):

            if i < 2:
                with col1:
                    if len(current_names[i]) > 25:
                        st.write(current_names[i][:24] + "..")
                    else:
                        st.write(current_names[i])
                    st.image(current_posters[i])
                    with st.expander("Get More Info"):
                        st.markdown("[{}](%s)".format(current_names[i]) % current_links[i])

            elif 1 < i < 4:
                with col2:
                    if len(current_names[i]) > 25:
                        st.write(current_names[i][:24] + "..")
                    else:
                        st.write(current_names[i])
                    st.image(current_posters[i])
                    with st.expander("Get More Info"):
                        st.markdown("[{}](%s)".format(current_names[i]) % current_links[i])
            elif 3 < i < 6:
                with col3:
                    if len(current_names[i]) > 25:
                        st.write(current_names[i][:24] + "..")
                    else:
                        st.write(current_names[i])
                    st.image(current_posters[i])
                    with st.expander("Get More Info"):
                        st.markdown("[{}](%s)".format(current_names[i]) % current_links[i])
            elif 5 < i < 8:
                with col4:
                    if len(current_names[i]) > 25:
                        st.write(current_names[i][:24] + "..")
                    else:
                        st.write(current_names[i])
                    st.image(current_posters[i])
                    with st.expander("Get More Info"):
                        st.markdown("[{}](%s)".format(current_names[i]) % current_links[i])
            elif 7 < i < 10:
                with col5:
                    if len(current_names[i]) > 25:
                        st.write(current_names[i][:24] + "..")
                    else:
                        st.write(current_names[i])
                    st.image(current_posters[i])
                    with st.expander("Get More Info"):
                        st.markdown("[{}](%s)".format(current_names[i]) % current_links[i])
    else:
        st.error("No Movies Left To Recommend.")
        st.success("Select a different movie to see its recommendations :)")
