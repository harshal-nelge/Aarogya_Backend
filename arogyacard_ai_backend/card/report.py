from google import genai
from google.genai import types
from google.cloud import storage
import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

# Set the path to the service account key JSON
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "service-account-key.json")

# Set your bucket name directly in the script
BUCKET_NAME = os.getenv("BUCKET_NAME")

def upload_to_gcs(file_path):
    """Uploads a file to Google Cloud Storage and returns a signed URL."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob_name = os.path.basename(file_path)  # Use the file name as the object name
    blob = bucket.blob(blob_name)

    # Upload the file
    blob.upload_from_filename(file_path)

    # Generate a signed URL valid for 7 days
    url = blob.generate_signed_url(
        expiration=timedelta(days=7),
        version="v4",
    )

    return url

def process_medical_report(file_path):
    """Function to process the medical report using Google Gemini API and store the file in GCS."""
    # Initialize Google Gemini API client
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    # Upload file to Google Gemini
    files = [client.files.upload(file=file_path)]
    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_uri(
                    file_uri=files[0].uri,
                    mime_type=files[0].mime_type,
                ),
                types.Part.from_text(text="Extract and summarize key medical information from this report."),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
        system_instruction=[
            types.Part.from_text(text="""You are an AI-powered medical assistant designed to extract, analyze, and summarize key medical information from medical reports..."""),
        ],
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        response_text += chunk.text

    # Upload the file to GCS and get the public URL
    file_url = upload_to_gcs(file_path)

    return {
        "summary": response_text,
        "file_url": file_url,
    }
