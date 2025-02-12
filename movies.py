import streamlit as st
import json
from groq import Groq

# Initialize Groq client
client = Groq()


def get_movie_recommendations(genre, exclude_names=None):
    """Calls Groq to get 5 movie recommendations."""
    system_msg = "You are a helpful assistant."
    if exclude_names:
        exclude_str = ", ".join(exclude_names)
        user_msg = (
            f"Recommend 5 movies based on the following genre/description: '{genre}'. "
            f"Do not include these movies: {exclude_str}. "
            "Return the answer as a JSON list of exactly 5 dictionaries, "
            "each with keys: 'name', 'description', 'genre', and 'rating'."
            "only generate list of json no text or ``` "
        )
    else:
        user_msg = (
            f"Recommend 5 movies based on the following genre/description: '{genre}'. "
            "Return the answer as a JSON list of exactly 5 dictionaries, "
            "each with keys: 'name', 'description', 'genre', and 'rating'."
            "only generate list of json no text or ``` "
        )

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )
    content = response.choices[0].message.content
    try:
        recommendations = json.loads(content)
        return recommendations
    except Exception as e:
        st.error("Error parsing recommendations.")
        return []


def show_movies_page():
    # Custom CSS for the movies page
    st.markdown("""
        <style>
        .movie-card {
            background-color: #E6E9EC;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 5px solid #68A5A4;
        }
        .movie-title {
            color: #1B2B31;
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .movie-genre {
            color: #68A5A4;
            font-style: italic;
            margin-bottom: 0.5rem;
        }
        .movie-description {
            color: #2F4F4F;
            line-height: 1.5;
        }
        .search-container {
            background-color: #E6E9EC;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header with custom styling
    st.markdown("<h1 style='color: #1B2B31; text-align: center; margin-bottom: 2rem;'>🎬 Movie Recommendations</h1>",
                unsafe_allow_html=True)

    # Search container
    with st.container():
        st.markdown("<div class='search-container'>", unsafe_allow_html=True)

        # Two-column layout for search
        col1, col2 = st.columns([3, 1])

        with col1:
            genre_input = st.text_input(
                "What kind of movie are you in the mood for?",
                placeholder="E.g., sci-fi adventure with time travel",
                key="movie_genre"
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing to align with input
            if st.button("🔍 Find Movies", key="get_movie_rec"):
                if genre_input:
                    with st.spinner("Finding perfect movies for you..."):
                        recommendations = get_movie_recommendations(
                            genre_input,
                            exclude_names=st.session_state.get("movie_exclusions", [])
                        )
                        st.session_state.movie_recommendations = recommendations
                        if "movie_exclusions" not in st.session_state:
                            st.session_state.movie_exclusions = []
                        for rec in recommendations:
                            name = rec.get("name")
                            if name and name not in st.session_state.movie_exclusions:
                                st.session_state.movie_exclusions.append(name)
                else:
                    st.warning("Please enter a genre or description.")

        st.markdown("</div>", unsafe_allow_html=True)

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🎲 Surprise Me", key="surprise_movie"):
            with st.spinner("Finding surprising movies..."):
                recommendations = get_movie_recommendations("surprise me with diverse genres")
                st.session_state.movie_recommendations = recommendations

    with col2:
        if st.button("⏭️ Next Set", key="next_movie"):
            if genre_input:
                with st.spinner("Finding more movies..."):
                    recommendations = get_movie_recommendations(
                        genre_input,
                        exclude_names=st.session_state.get("movie_exclusions", [])
                    )
                    if "movie_exclusions" not in st.session_state:
                        st.session_state.movie_exclusions = []
                    for rec in recommendations:
                        name = rec.get("name")
                        if name and name not in st.session_state.movie_exclusions:
                            st.session_state.movie_exclusions.append(name)
                    st.session_state.movie_recommendations = recommendations

    with col3:
        if st.button("🔄 Start Over", key="reset_movie"):
            st.session_state.movie_exclusions = []
            st.session_state.movie_recommendations = []
            st.experimental_rerun()

    # Display recommendations
    if "movie_recommendations" in st.session_state and st.session_state.movie_recommendations:
        st.markdown("### 🎯 Here are your personalized recommendations:")

        for rec in st.session_state.movie_recommendations:
            st.markdown(f"""
                <div class='movie-card'>
                    <div class='movie-title'>{rec.get('name', 'N/A')}</div>
                    <div class='movie-genre'>🎭 {rec.get('genre', 'N/A')}</div>
                    <div class='movie-description'>{rec.get('description', 'N/A')}</div>
                </div>
            """, unsafe_allow_html=True)