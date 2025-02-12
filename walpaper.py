import streamlit as st
import os
import requests
import json
import base64
import shutil

# API Key (Replace with your actual key)
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Temporary directory for downloaded images
TEMP_DIR = "temp"

# Ensure the temp directory exists
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)


# Function to search for wallpapers
def fetch_wallpapers(query):
    url = "https://google.serper.dev/images"
    payload = json.dumps({"q": f"{query} wallpaper", "num": 30})  # Limiting to 30 images for performance
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    try:
        results = response.json()
        images = [item["imageUrl"] for item in results.get("images", [])]
        return images if images else None
    except Exception as e:
        return None


# Function to download image and provide a direct download link
def get_image_download_link(img_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(img_url, headers=headers)

    if response.status_code == 200:
        file_name = img_url.split("/")[-1].split("?")[0]  # Extract filename
        file_path = os.path.join(TEMP_DIR, file_name)

        # Save image locally
        with open(file_path, "wb") as file:
            file.write(response.content)

        # Convert to Base64
        with open(file_path, "rb") as file:
            b64 = base64.b64encode(file.read()).decode()

        # Delete the file after creating the link
        os.remove(file_path)

        return f'<a href="data:image/jpeg;base64,{b64}" download="{file_name}">📥 Download</a>'
    else:
        return None  # Return None if download fails


# Function to clean up all files (if needed)
def clean_temp_folder():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)  # Delete entire temp folder
        os.makedirs(TEMP_DIR)  # Recreate it


# UI Layout
def show_wallpaper_page():
    st.title("🖼️ Search Wallpapers for Movies & Series")

    query = st.text_input("Enter a movie or series name:", key="wallpaper_query")

    if st.button("Search"):
        if query:
            with st.spinner("Fetching wallpapers..."):
                images = fetch_wallpapers(query)

            if images:
                st.success(f"✅ Found {len(images)} wallpapers!")

                # Display images in a grid with download links
                cols = st.columns(3)
                for index, img_url in enumerate(images):
                    with cols[index % 3]:
                        st.image(img_url, use_container_width=True)  # Display image

                        # Direct download link
                        download_link = get_image_download_link(img_url)
                        if download_link:
                            st.markdown(download_link, unsafe_allow_html=True)
                        else:
                            st.error("❌ Failed to generate download link.")

                # Cleanup temp files
                clean_temp_folder()
            else:
                st.error("❌ No wallpapers found. Try another name.")
        else:
            st.warning("Please enter a name.")
