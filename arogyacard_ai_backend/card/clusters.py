import requests
from bs4 import BeautifulSoup
import urllib3
import os
import tempfile
import json
from PyPDF2 import PdfReader, PdfWriter
from google import genai
from google.genai import types
import googlemaps
from dotenv import load_dotenv

load_dotenv()

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_pdf(pdf_url):
    # Download the PDF from the given URL
    pdf_response = requests.get(pdf_url, verify=False)
    if pdf_response.status_code != 200:
        return None, f"Failed to download PDF: {pdf_response.status_code}"
    
    # Save the PDF to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
        temp_pdf.write(pdf_response.content)
        temp_pdf_path = temp_pdf.name
    return temp_pdf_path, None

def get_outbreak_data(year, week_number):
    # Fetch the webpage content
    url = "https://idsp.mohfw.gov.in/index4.php?lang=1&level=0&linkid=406&lid=3689"
    response = requests.get(url, verify=False)
    
    if response.status_code != 200:
        return f"Failed to fetch the page: {response.status_code}"
    
    # Parse the HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table
    table = soup.find('table')
    if not table:
        return "Table not found"
    
    # Find the row containing the specified year
    target_row = None
    for row in table.find_all('tr'):
        # Find cells in the row
        cells = row.find_all('td')
        if not cells:
            continue
            
        # Check if the first cell contains the target year
        if cells[0].get_text().strip() == str(year):
            target_row = row
            break
    
    if not target_row:
        return f"Year {year} not found in the table"
    
    # Get all links in the second cell (contains week links)
    week_links = target_row.find_all('td')[1].find_all('a')
    
    # Find the link that corresponds to the specified week
    pdf_url = None
    for link in week_links:
        # Check if the link text contains the week number we want
        link_text = link.get_text().strip()
        if link_text == f"{week_number}th" or link_text == f"{week_number}st" or link_text == f"{week_number}nd" or link_text == f"{week_number}rd":
            pdf_url = link.get('href')
            break
    
    if not pdf_url:
        return f"Week {week_number} not found for year {year}"
    
    # Check if the PDF URL is a valid Google Drive URL and convert to direct download
    if "drive.google.com" in pdf_url:
        # print(f"Detected Google Drive URL: {pdf_url}")
        file_id = pdf_url.split('/d/')[1].split('/')[0]
        pdf_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    # Download the PDF and return the path
    pdf_path, error = download_pdf(pdf_url)
    if error:
        return error
    
    result = remove_first_pages(pdf_path, 2)
    final_result = analyze_pdf_with_gemini(result)
    return final_result
  


def remove_first_pages(pdf_path, num_pages_to_remove):
    """Remove the first n pages from a PDF file"""
    pdf_reader = PdfReader(pdf_path)
    pdf_writer = PdfWriter()
    
    # Add all pages except the first num_pages_to_remove
    for page_num in range(num_pages_to_remove, len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page_num])
    
    # Create new PDF file without the first pages
    processed_pdf_path = f"{pdf_path.split('.')[0]}_processed.pdf"
    with open(processed_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)
    
    return processed_pdf_path

def convert_to_map_format(outbreak_data):
    """Convert the Gemini response to the required map format with geocoding"""
    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=os.getenv("GOOGLE_PLACES_API_KEY"))
    
    map_outbreaks = []
    
    for outbreak in outbreak_data.get("outbreaks", []):
        district = outbreak.get("district")
        disease = outbreak.get("disease")
        cases = outbreak.get("cases", 0)
        
        # Get coordinates from Google Maps Geocoding API
        try:
            geocode_result = gmaps.geocode(f"{district}, India")
            if geocode_result and len(geocode_result) > 0:
                location = geocode_result[0]["geometry"]["location"]
                lat = location["lat"]
                lng = location["lng"]
                
                # Calculate radius based on cases
                radius = cases * 5
                
                map_outbreaks.append({
                    "center": [lat, lng],
                    "radius": radius,
                    "name": f"{disease} Outbreak",
                    "cases": cases
                })
        except Exception as e:
            print(f"Error geocoding {district}: {e}")
    
    # Format the final output
    output = {"outbreaks": map_outbreaks}
    out = json.dumps(output, indent=2)
    return out


def analyze_pdf_with_gemini(file_path):
    """Send the PDF to Gemini Flash for analysis"""
    # Initialize Google Gemini API client
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )
    
    # Upload file to Google Gemini
    files = [client.files.upload(file=file_path)]
    model = "gemini-2.0-flash"
    
    # Create prompt for extracting disease outbreaks by district
    contents = [
        types.Content(  # Use types.Content instead of Content
            role="user",
            parts=[
                types.Part.from_uri(  # Use types.Part instead of Part
                    file_uri=files[0].uri,
                    mime_type=files[0].mime_type,
                ),
                types.Part.from_text(text="""Extract information about disease outbreaks from this report. 
                For each outbreak, identify:
                1. District/location name
                2. Disease name
                3. Number of cases
                
                Return the data strictly in the following JSON format. If any data of a district is missing, skip that entry. This format must be maintained:
                
                {
                  "outbreaks": [
                    {
                      "district": "Vizianagaram",
                      "disease": "Acute Diarrheal Disease",
                      "cases": 15
                    },
                    {
                      "district": "East Kameng",
                      "disease": "Human Rabies",
                      "cases": 1
                    },
                    {
                      "district": "Thrissur",
                      "disease": "Food Poisoning",
                      "cases": 107
                    }
                  ]
                }
                """),
            ],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        temperature=0.1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
    )
    
    # Get response from Gemini
    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text

    # Parse the complete response into JSON
    try:
        outbreak_data = json.loads(response_text)
    except json.JSONDecodeError:
        print("Failed to parse Gemini response as JSON")
        return {"error": "Failed to parse Gemini response as JSON"}
    
    # Convert to map format
    try:
        result = convert_to_map_format(outbreak_data)
        return result
    except Exception as e:
        print(f"Error converting outbreak data to map format: {e}")
        return {"error": f"Error converting outbreak data to map format: {e}"}



