import streamlit as st
import os
import requests
import json
from groq import Groq

# API Keys (Replace these with your actual keys)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Initialize Groq client
client = Groq()


def search_movie_or_series(title, content_type):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": title + " " + content_type})
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)
    try:
        results = response.json()
        links = [item["link"] for item in results.get("organic", []) if "imdb.com" in item["link"]]
        return links[0] if links else None
    except Exception:
        return None


def scrape_page(url):
    api_url = "https://scrape.serper.dev"
    payload = json.dumps({"url": url})
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

    response = requests.request("POST", api_url, headers=headers, data=payload)
    try:
        return response.json()
    except Exception:
        return None


def preprocess_with_groq(content):
    system_msg = "You are an expert at summarizing movie and series details."
    user_msg = f"Summarize the following movie/series information into a clean format:\n\n{content}"

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )

    return response.choices[0].message.content


def show_search_page():
    st.title("🎬 Search for a Movie or Series")

    # Fix image display issue
    st.image("https://source.unsplash.com/800x400/?cinema,movie", use_container_width=True)

    # Layout: Text input and Dropdown in the same row
    col1, col2 = st.columns([3, 1])  # Wider input, smaller dropdown
    with col1:
        title_input = st.text_input("Enter a movie or series title:", key="search_title")
    with col2:
        content_type = st.selectbox("Type", ["Movie", "Drama"])

    # Search button
    if st.button("Search"):
        if title_input:
            with st.spinner("Searching..."):
                imdb_link = search_movie_or_series(title_input, content_type)

            if imdb_link:
                st.success(f"✅ IMDb Link: [Click Here]({imdb_link})")

                with st.spinner("Extracting details..."):
                    scraped_content = scrape_page(imdb_link)

                if scraped_content:
                    # Extract thumbnail (poster) if available
                    thumbnail_url = scraped_content.get("metadata", None)
                    thumbnail_url = thumbnail_url.get("og:image", None)
                    print(thumbnail_url)

                    if thumbnail_url:
                        st.image(thumbnail_url, caption="Movie Poster", use_container_width=False, width=300)

                    with st.spinner("Processing with AI..."):
                        processed_info = preprocess_with_groq(str(scraped_content))

                    st.markdown("### 🎭 Movie/Series Details")
                    st.markdown(processed_info)
                else:
                    st.warning("Could not extract content.")
            else:
                st.error("❌ Didn't find the IMDb link.")
        else:
            st.warning("Please enter a title.")


# Run the app
show_search_page()
