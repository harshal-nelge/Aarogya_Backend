from google import genai
from google.genai import types

def process_medical_report(file_path):
    """Function to process the medical report using Google Gemini API"""
    client = genai.Client(api_key='AIzaSyBQa8QQmA_tAZjR0LyF2jHivjuKu8Q6rAY')

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

    return {"summary": response_text}
