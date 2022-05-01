import streamlit as st
import pandas as pd
import numpy as np
import pickle
from sklearn.neighbors import NearestNeighbors
import plotly.express as px
import streamlit.components.v1 as components
import random


def app():
    # ==================================Caching the data to give faster results========================================#
    #@st.cache(allow_output_mutation=True)
    def load_data():
        og_df = df = pickle.load(open("MusicRecommender/filtered_track_df.pkl", "rb"))
        df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
        og_df['genres'] = df.genres.apply(lambda x: [i[1:-1] for i in str(x)[1:-1].split(", ")])
        exploded_track_df = df.explode("genres")
        # Genre has been exploded because it has values like [pop, hiphop, electronic] so it splits
        # into multiple rows with same indexing
        return og_df, exploded_track_df

    genre_names = ['Dance Pop', 'Electronic', 'Electropop', 'Hip Hop', 'Jazz', 'K-pop', 'Latin', 'Pop', 'Pop Rap',
                   'R&B', 'Rock', 'Bollywood']
    audio_features = ["acousticness", "danceability", "energy", "instrumentalness", "valence", "tempo"]
    og_df, exploded_track_df = load_data()

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
                 background: url("https://images.pexels.com/photos/268533/pexels-photo-268533.jpeg");
                 background-size: cover;
             }}
             </style>
             """,
            unsafe_allow_html=True
        )

    # =========================Implementing The KNN(K- NearestNeighbors Algorithm)======================================#
    def n_neighbors_uri_audio(search_type, sortby, genre, start_year, end_year, test_feat):

        # Sorting according to the popularity and genre
        artist_index = []
        genre = genre.lower()
        genre_data = exploded_track_df[(exploded_track_df['genres'] == genre)
                                       & (exploded_track_df["release_year"] >= start_year)
                                       & (exploded_track_df["release_year"] <= end_year)
                                       ]
        genre_data = genre_data.sort_values(by=sortby, ascending=False)[0:500]
        if search_type[0] == 1:
            artist_data = og_df[(og_df['artists_name'] == artist)]
            artist_data = artist_data.sort_values(by=sortby, ascending=False)
            a_index = artist_data.index.tolist()
            artist_index = og_df.iloc[a_index]["uri"].tolist()

        # Creating object for Nearest Neighbor
        neigh = NearestNeighbors()
        neigh.fit(genre_data[audio_features].to_numpy())
        n_neighbors = neigh.kneighbors([test_feat], n_neighbors=len(genre_data), return_distance=False)[0]
        uris = artist_index + genre_data.iloc[n_neighbors]["uri"].to_list()
        audios = genre_data.iloc[n_neighbors][audio_features].to_numpy()
        return uris, audios

    # ==========================================App Layout and Integration=============================================#
    set_bg()
    music_emojis = ["🎶", "🎸", "🎹", "📯", "📻", "🎧"]
    st.title("{}Music Recommender System".format(random.choice(music_emojis)))
    st.markdown("Getting Bored? Listen to some music. Here, you can customize the system according to your taste. You "
                "can play around with the different settings and see what recommendations we have to offer :)")

    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            song_list = pickle.load(open("MusicRecommender/songs_list.pkl", "rb"))
            songs_list = ["Search here..."]
            songs_list += song_list
            song_info = st.selectbox('Search for an artist or a song,',
                                     songs_list,
                                     index=0)
        with col2:
            sortby = st.multiselect("Sort by,", ['popularity', 'release_year'])
    st.subheader("Enjoy the recommendations below,")
    # =================================================================================================================#
    # PreDefining values for the audio features
    genre_list = ['dance pop', 'electronic', 'electropop', 'hip hop', 'jazz', 'k-pop', 'latin', 'pop', 'pop rap', 'r&b',
                  'rock', 'bollywood']
    s_year, acoustic, dance, energ, instrumental, valen, temp, gen = 2005, 0.5, 0.5, 0.5, 0.5, 0.5, 146.0, 7
    search_type = [0, song_info]
    if song_info != "Search here...":
        if '-' in song_info:
            def find_gen(secret_list):
                for g in secret_list:
                    if g in genre_list:
                        return genre_list.index(g)

            info = og_df.loc[og_df['song_artist'] == song_info].index[0]
            s_year = og_df.iloc[info].release_year
            acoustic = og_df.iloc[info].acousticness
            dance = og_df.iloc[info].danceability
            energ = og_df.iloc[info].energy
            instrumental = og_df.iloc[info].instrumentalness
            valen = og_df.iloc[info].valence
            temp = og_df.iloc[info].tempo

            # For Finding Genre
            if isinstance(exploded_track_df.loc[info].genres, str):
                mystery = [exploded_track_df.loc[info].genres]
            else:
                mystery = exploded_track_df.loc[info].genres.unique().tolist()

            gen = find_gen(mystery)
        else:
            artist = song_info
            search_type = [1, artist]

    # =================================================================================================================#

    # Creating Options In the sidebar
    with st.sidebar.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.sidebar.subheader("Customize Here,")
        with col2:
            with st.sidebar.expander("Choose Your Audio Features"):
                st.caption("Note:- (0 - less likely | 1 - most likely)")
                start_year, end_year = st.slider('Select the year range', 1950, 2019, (int(s_year), 2019))
                acousticness = st.slider("Acoustic - Song's Acousticness", 0.0, 1.0, float(acoustic),
                                         help="This value describes how acoustic a song is. A score of 1.0 means the "
                                              "song is most likely to be an acoustic one.")
                danceability = st.slider("Dance - Song's Danceability", 0.0, 1.0, float(dance),
                                         help="Danceability describes how suitable a track is for dancing based on a "
                                              "combination of musical elements including tempo, rhythm stability, "
                                              "beat strength, and overall regularity. A value of 0.0 is least "
                                              "danceable and 1.0 is most danceable.")
                energy = st.slider("Energy - Song's Energy", 0.0, 1.0, float(energ),
                                   help="(Energy) represents a perceptual measure of intensity and activity. "
                                        "Typically, energetic tracks feel fast, loud, and noisy.")
                instrumentalness = st.slider("Instrumental - Song's Instrumentalness", 0.0, 1.0,
                                             float(instrumental),
                                             help="This value represents the amount of vocals in the song. The closer "
                                                  "it is to 1.0, the more instrumental the song is.")
                valence = st.slider("Valence - Song's Positiveness", 0.0, 1.0, float(valen),
                                    help="A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a "
                                         "track. Tracks with high valence sound more positive (e.g. happy, cheerful, "
                                         "euphoric), while tracks with low valence sound more negative (e.g. sad, "
                                         "depressed, angry).")
                tempo = st.slider("Tempo - Song's Rhythm", 0.0, 244.0, float(temp),
                                  help="The overall estimated tempo of a track in beats per minute (BPM). In musical "
                                       "terminology, tempo is the speed or pace of a given piece, and derives "
                                       "directly from the average beat duration.")
        with col3:
            with st.sidebar.expander("Choose Your Genre"):
                genre = st.radio("Select your favourite:", genre_names, index=gen)

    # =======================================Passing the values to the function=======================================#

    tracks_per_page = 10
    test_feat = [acousticness, danceability, energy, instrumentalness, valence, tempo]

    # calling the function --> neighbors
    uris, audios = n_neighbors_uri_audio(search_type, sortby, genre, start_year, end_year, test_feat)
    tracks = []
    for uri in uris:
        track = """<iframe style="border-radius:12px" src="https://open.spotify.com/embed/track/{}" width="100%" 
        height="80" frameborder="0" allowtransparency="true" allow="autoplay; clipboard-write; encrypted-media; 
        fullscreen; picture-in-picture"></iframe>""".format(uri)
        tracks.append(track)

    # ================================================================================================================#
    # Checking Current Session
    if 'previous_inputs' not in st.session_state:
        st.session_state['previous_inputs'] = [genre, start_year, end_year] + test_feat
    current_input = [genre, start_year, end_year] + test_feat
    if current_input != st.session_state['previous_inputs']:
        if 'start_track_i' in st.session_state:
            st.session_state['start_track_i'] = 0
        st.session_state['previous_inputs'] = current_input

    if 'start_track_i' not in st.session_state:
        st.session_state['start_track_i'] = 0

    # =======================Recommending Songs With A Graph Of Its Features To The User===============================#
    with st.container():
        col1, col2 = st.columns([2, 2])
        if st.button("Get More Songs"):
            if st.session_state['start_track_i'] < len(tracks):
                st.session_state['start_track_i'] += tracks_per_page

    current_tracks = tracks[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]
    current_audios = audios[st.session_state['start_track_i']: st.session_state['start_track_i'] + tracks_per_page]

    if st.session_state['start_track_i'] < len(tracks):
        h = 90
        for i, (track, audio) in enumerate(zip(current_tracks, current_audios)):
            if i < 5:
                with col1:
                    components.html(
                        track,
                        height=h
                    )
                    with st.expander("See Feature Chart Details"):
                        df = pd.DataFrame(dict(
                            r=audio[:5],
                            theta=audio_features[:5]
                        ))
                        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                        fig.update_layout(height=250, width=475)
                        st.plotly_chart(fig)

            else:
                with col2:
                    components.html(
                        track,
                        height=h
                    )

                    with st.expander("See Feature Chart Details"):
                        df = pd.DataFrame(dict(
                            r=audio[:5],
                            theta=audio_features[:5]
                        ))
                        fig = px.line_polar(df, r='r', theta='theta', line_close=True)
                        fig.update_layout(height=250, width=475)
                        st.plotly_chart(fig)
    else:
        st.error("No more songs to recommend :(")
    # =======================END: MAYBE OR MAYBE NOT=============================#

