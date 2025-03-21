from eventregistry import *
import os

def get_news(city, country=None, max_items=500):
    """
    Fetch news about diseases and pollution for a specific city.
    API key is fetched from environment variables.
    
    Parameters:
    city (str): City to search for news about
    country (str): Country of the city (optional, improves location resolution)
    max_items (int): Maximum number of articles to return
    
    Returns:
    list: List of article objects
    """
    # Get API key from environment variables
    api_key = os.environ.get("EVENT_REGISTRY_API_KEY")
    if not api_key:
        raise ValueError("EVENT_REGISTRY_API_KEY environment variable not set")
        
    er = EventRegistry(apiKey=api_key)
    
    # Get location URI for the city
    location_query = city
    if country:
        location_query += ", " + country
    city_uri = er.getLocationUri(location_query)
    
    # Query for disease and pollution news related to the city
    query = QueryArticlesIter(
        keywords=QueryItems.OR(["disease", "epidemic", "outbreak", "virus", "infection", 
                               "pollution", "air quality", "water contamination", 
                               "environmental hazard"]),
        locationUri=city_uri,  # Articles mentioning this location
        dataType=["news"]
    )
    
    # Collect articles in a list
    articles = []
    for art in query.execQuery(er, sortBy="date", maxItems=max_items):
        articles.append(art)
    
    return articles

