import streamlit as st


# Defining the multipage class to manage the multiple apps in program
class MultiPage:
    def __init__(self) -> None:
        self.pages = []

    def add_page(self, title, func) -> None:
        self.pages.append({
            "title": title,
            "function": func
        })

    def run(self):
        # Dropdown to select the page to run
        st.sidebar.subheader("What's the mood today? Movies or Music?")
        page = st.sidebar.selectbox(
            "Choose from below,",
            self.pages,
            format_func=lambda page: page['title']
        )

        page['function']()
