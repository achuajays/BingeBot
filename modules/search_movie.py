import streamlit as st
import requests
import json
import os

# API Key (Replace with your actual key)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Function to search for videos
def fetch_videos(query):
    url = "https://google.serper.dev/videos"
    payload = json.dumps({"q": query, "num": 10})  # Fetch up to 10 results
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    try:
        results = response.json()
        return results.get("videos", [])
    except Exception as e:
        return None

# UI Layout
def show_video_search_page():
    st.title("🎥 Search for Videos")

    query = st.text_input("Enter a video search term:", key="video_query")

    if st.button("Search"):
        if query:
            with st.spinner("Searching for videos..."):
                videos = fetch_videos(query)

            if videos:
                st.success(f"✅ Found {len(videos)} videos!")

                # Display videos in a structured layout
                for video in videos:
                    title = video.get("title", "Unknown Title")
                    link = video.get("link", "#")
                    thumbnail = video.get("thumbnailUrl", video.get("imageUrl", ""))
                    duration = video.get("duration", "Unknown Duration")
                    source = video.get("source", "Unknown Source")
                    channel = video.get("channel", "Unknown Channel")
                    date = video.get("date", "Unknown Date")

                    col1, col2 = st.columns([1, 3])  # Thumbnail on left, details on right
                    with col1:
                        if thumbnail:
                            st.image(thumbnail, use_container_width=True)
                    with col2:
                        st.markdown(f"### 🎬 [{title}]({link})")
                        st.markdown(f"📺 **Channel:** {channel}  \n⏳ **Duration:** {duration}  \n📅 **Published on:** {date}  \n🌐 **Source:** {source}")

                    st.markdown("---")  # Separator for clarity
            else:
                st.error("❌ No videos found. Try another keyword.")
        else:
            st.warning("⚠️ Please enter a search term.")
