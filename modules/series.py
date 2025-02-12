import streamlit as st
import json
from groq import Groq

# Initialize Groq client
client = Groq()


def get_series_recommendations(genre, exclude_names=None):
    """Calls Groq to get 5 series recommendations."""
    system_msg = "You are a helpful assistant."
    if exclude_names:
        exclude_str = ", ".join(exclude_names)
        user_msg = (
            f"Recommend 5 TV series based on the following genre/description: '{genre}'. "
            f"Do not include these series: {exclude_str}. "
            f"if no other drama other than {exclude_str} exist, return 'no other drama other than {exclude_str} exist'. "
            "Return the answer as a JSON list of exactly 5 dictionaries, "
            "each with keys: 'name', 'description', 'genre', and 'seasons'."
            "only generate list of json no text or ``` "
            f"remember never recommend a series in {exclude_str} ."
        )
    else:
        user_msg = (
            f"Recommend 5 TV series based on the following genre/description: '{genre}'. "
            "Return the answer as a JSON list of exactly 5 dictionaries, "
            "each with keys: 'name', 'description', 'genre', and 'seasons'."
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


def show_series_page():
    # Custom CSS for the series page
    st.markdown("""
        <style>
        .series-card {
            background-color: #E6E9EC;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 5px solid #1B2B31;
        }
        .series-title {
            color: #1B2B31;
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .series-genre {
            color: #68A5A4;
            font-style: italic;
            margin-bottom: 0.5rem;
        }
        .series-description {
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
    st.markdown("<h1 style='color: #1B2B31; text-align: center; margin-bottom: 2rem;'>📺 TV Series Recommendations</h1>",
                unsafe_allow_html=True)

    # Search container
    with st.container():
        st.markdown("<div class='search-container'>", unsafe_allow_html=True)

        # Two-column layout for search
        col1, col2 = st.columns([3, 1])

        with col1:
            genre_input = st.text_input(
                "What kind of series would you like to watch?",
                placeholder="E.g., mystery drama with strong character development",
                key="series_genre"
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Spacing to align with input
            if st.button("🔍 Find Series", key="get_series_rec"):
                if genre_input:
                    with st.spinner("Finding perfect series for you..."):
                        recommendations = get_series_recommendations(
                            genre_input,
                            exclude_names=st.session_state.get("series_exclusions", [])
                        )
                        st.session_state.series_recommendations = recommendations
                        if "series_exclusions" not in st.session_state:
                            st.session_state.series_exclusions = []
                        for rec in recommendations:
                            name = rec.get("name")
                            if name and name not in st.session_state.series_exclusions:
                                st.session_state.series_exclusions.append(name)
                else:
                    st.warning("Please enter a genre or description.")

        st.markdown("</div>", unsafe_allow_html=True)

    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("🎲 Surprise Me", key="surprise_series"):
            with st.spinner("Finding surprising series..."):
                recommendations = get_series_recommendations("surprise me with diverse genres")
                st.session_state.series_recommendations = recommendations

    with col2:
        if st.button("⏭️ Next Set", key="next_series"):
            if genre_input:
                with st.spinner("Finding more series..."):
                    recommendations = get_series_recommendations(
                        genre_input,
                        exclude_names=st.session_state.get("series_exclusions", [])
                    )
                    if "series_exclusions" not in st.session_state:
                        st.session_state.series_exclusions = []
                    for rec in recommendations:
                        name = rec.get("name")
                        if name and name not in st.session_state.series_exclusions:
                            st.session_state.series_exclusions.append(name)
                    print(st.session_state.get("series_exclusions", []))
                    st.session_state.series_recommendations = recommendations

    with col3:
        if st.button("🔄 Start Over", key="reset_series"):
            st.session_state.series_exclusions = []
            st.session_state.series_recommendations = []
            st.rerun()

    # Display recommendations
    if "series_recommendations" in st.session_state and st.session_state.series_recommendations:
        st.markdown("### 🎯 Here are your personalized recommendations:")

        for rec in st.session_state.series_recommendations:
            st.markdown(f"""
                <div class='series-card'>
                    <div class='series-title'>{rec.get('name', 'N/A')}</div>
                    <div class='series-genre'>🎭 {rec.get('genre', 'N/A')}</div>
                    <div class='series-description'>{rec.get('description', 'N/A')}</div>
                </div>
            """, unsafe_allow_html=True)