import Music_Recommender
import Movies_Recommender
import streamlit as st
import random
from multipage import MultiPage

favicon = ["🎶", "🎸", "🎹", "📯", "📻", "🎧", "🍿", "🎥", "🎞", "🎬", "📺", "📽"]
st.set_page_config(page_title="Movies & Music Recommender", page_icon=random.choice(favicon), layout="wide")
# hiding the menu from the app
hide_menu_style = f"""
        <style>
        .st-ae{{caret-color: transparent;}}
        #MainMenu {{visibility: visible;}}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

app = MultiPage()

# Adding pages on the sidebar here
app.add_page("Movies", Movies_Recommender.app)
app.add_page("Music", Music_Recommender.app)


app.run()
