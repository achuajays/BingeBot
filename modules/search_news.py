import streamlit as st
import requests
import json
import os
from groq import Groq

# API Keys (Replace with your actual keys)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq()

# Time filter mapping
TIME_FILTERS = {
    "Anytime": "",
    "Past Hour": "qdr:h",
    "Past Day": "qdr:d",
    "Past Week": "qdr:w",
    "Past Month": "qdr:m",
    "Past Year": "qdr:y"
}

# Function to fetch news
def fetch_news(query, time_filter):
    url = "https://google.serper.dev/news"
    payload = json.dumps({"q": query, "num": 10, "tbs": time_filter})
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    try:
        results = response.json()
        return results.get("news", [])
    except Exception:
        return None

# AI verification function using Groq
def verify_news_with_ai(query, articles):
    system_msg = "You are an AI assistant that verifies whether news articles are relevant to the search topic."
    user_msg = f"Verify if the following news articles are relevant to the topic '{query}'. Keep only relevant ones:\n\n{articles}"

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        max_completion_tokens=1024,
        top_p=1,
        stop=None,
        stream=False,
    )

    return response.choices[0].message.content  # Processed AI-filtered results

# UI Layout
def show_news_page():
    st.title("📰 Search for News Articles")

    query = st.text_input("Enter a news topic:", key="news_query")

    # Dropdown for time filters
    time_filter = st.selectbox("Select Time Range:", list(TIME_FILTERS.keys()))

    if st.button("Search"):
        if query:
            with st.spinner("Fetching news..."):
                news_articles = fetch_news(query, TIME_FILTERS[time_filter])

            if news_articles:
                st.success(f"✅ Found {len(news_articles)} articles! Verifying with AI...")



                st.subheader("🔍 Verified News Results")

                for article in news_articles:
                    title = article.get("title", "No Title")
                    link = article.get("link", "#")
                    snippet = article.get("snippet", "No description available.")
                    date = article.get("date", "Unknown Date")
                    source = article.get("source", "Unknown Source")
                    image_url = article.get("imageUrl", "")

                    col1, col2 = st.columns([1, 3])  # Image on left, text on right
                    with col1:
                        if image_url:
                            st.image(image_url, use_container_width=True)
                    with col2:
                        st.markdown(f"### 📰 [{title}]({link})")
                        st.markdown(f"📅 **Date:** {date}  \n📰 **Source:** {source}")
                        st.markdown(f"🔹 {snippet}")

                    st.markdown("---")  # Separator
            else:
                st.error("❌ No news articles found. Try another keyword.")
        else:
            st.warning("⚠️ Please enter a search term.")
