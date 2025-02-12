import streamlit as st


# Configure the page with custom styling
st.set_page_config(
    page_title="Movie & Series Recommender",
    layout="wide",
    initial_sidebar_state="expanded"
)


from modules.search import show_search_page
from modules.walpaper import show_wallpaper_page
from modules.search_movie import show_video_search_page
from modules.search_news import show_news_page
from modules.movies import show_movies_page
from modules.series import show_series_page

# Custom CSS
st.markdown("""
    <style>
    .stButton > button {
        background-color: #1B2B31;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #68A5A4;
        color: white;
    }
    .sidebar .sidebar-content {
        background-color: #E6E9EC;
    }
    h1, h2, h3 {
        color: #1B2B31;
    }
    .stTextInput > div > div > input {
        background-color: white;
        color: #2F4F4F;
        border: 1px solid #68A5A4;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar with custom styling
with st.sidebar:
    st.title("Navigation")
    page = st.radio(
        "Go to",
        ["Movies", "Series","Search", "Wallpaper","Video Search","News"],
        key="navigation"
    )

if page == "Movies":
    show_movies_page()
elif page == "Series":
    show_series_page()
elif page == "Search":
    show_search_page()
elif page == "Wallpaper":
    show_wallpaper_page()
elif page == "Video Search":
    show_video_search_page()
elif page == "News":
    show_news_page()

