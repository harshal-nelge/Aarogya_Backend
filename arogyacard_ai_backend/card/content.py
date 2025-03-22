import requests
from .models import ChatHistory, DiagnosedDisease
from dotenv import load_dotenv
import os
load_dotenv()

# YouTube API Key
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Google Custom Search Engine ID
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

def get_disease_by_hid(hid):
    """
    Fetch the most recently diagnosed disease for the given ChatHistory ID (hid).
    """
    try:
        chat_history = ChatHistory.objects.get(hid=hid)
        # Retrieve the latest diagnosed disease for the chat history
        disease_entry = DiagnosedDisease.objects.filter(hid=chat_history).order_by("-created_at").first()
        return disease_entry.disease if disease_entry else None
    except ChatHistory.DoesNotExist:
        return None


def fetch_youtube_videos(disease, max_results=5):
    """
    Fetch YouTube videos for the given disease using the YouTube Data API.
    """
    youtube_search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{disease} tips OR treatment OR motivation",  # Improved query structure
        "type": "video",
        "videoDuration": "any",  # Allow any video duration for broader results
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY,
    }

    # Send the GET request to YouTube API
    response = requests.get(youtube_search_url, params=params)

    # Debugging logs for the API request and response
    print(f"API URL: {response.url}")
    print(f"Response Code: {response.status_code}")
    
    try:
        video_data = response.json()
        print(f"Response JSON: {video_data}")  # Debugging log
    except ValueError:
        print("Error: Invalid JSON response from YouTube API.")
        return {"error": "Invalid JSON response from YouTube API."}

    # Handle non-200 status codes
    if response.status_code != 200:
        return {"error": f"Failed to fetch data from YouTube API. Status Code: {response.status_code}"}

    # Extract video recommendations
    recommendations = []
    for item in video_data.get("items", []):
        recommendations.append({
            "title": item["snippet"]["title"],
            "description": item["snippet"]["description"],
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        })

    # If no videos found, return a friendly message
    if not recommendations:
        return {"error": f"No videos found for the disease: {disease}"}

    return recommendations


def fetch_google_articles(disease, max_results=5):
    """
    Fetch personalized articles for the given disease using Google Custom Search JSON API.
    """
    google_cse_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": YOUTUBE_API_KEY,  # Use the same API key as YouTube
        "cx": SEARCH_ENGINE_ID,
        "q": f"{disease} tips OR treatment OR motivation",
        "num": max_results,
        "safe": "active",  # Filter explicit content
    }

    try:
        # Make the API request
        response = requests.get(google_cse_url, params=params)
        response.raise_for_status()  # Raise an error for unsuccessful status codes

        # Parse the response JSON
        search_results = response.json()
        articles = []

        # Extract relevant article details
        for item in search_results.get("items", []):
            articles.append({
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "url": item.get("link"),
                "source": item.get("displayLink"),
            })

        return articles

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def fetch_content(hid):
    """
    Fetch relevant content (YouTube videos and Google articles) for the diagnosed disease
    associated with the given ChatHistory ID (hid).
    """
    # Fetch the disease associated with the given HID
    disease = get_disease_by_hid(hid)
    if not disease:
        return {"error": f"No disease found for HID '{hid}'."}

    # Fetch YouTube videos and Google articles
    youtube_videos = fetch_youtube_videos(disease)
    google_articles = fetch_google_articles(disease)

    return {
        "disease": disease,
        "youtube_videos": youtube_videos,
        "google_articles": google_articles,
    }
