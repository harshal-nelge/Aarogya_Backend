from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from .models import ChatHistory
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

# Get API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

# Initialize LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=500,
    timeout=10,
    max_retries=2,
)

# Chat Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are a conversational medical chatbot. Gather sufficient information by asking follow-up questions "
     "before providing a diagnosis. Ask 3-4 relevant follow-up questions based on the user's symptoms to ensure "
     "you have enough information to provide a helpful assessment.\n\n"
     "Examples of good follow-up questions:\n"
     "- If the user mentions fever: 'How many days have you had a fever? Is it accompanied by other symptoms?'\n"
     "- If the user reports chest pain: 'Do you also feel shortness of breath or dizziness? Where exactly is the pain located?'\n"
     "- If the user has a headache: 'Is it a throbbing pain or more like pressure? Does light or sound make it worse?'\n"
     "- If the user mentions stomach pain: 'Is the pain constant or intermittent? Have you noticed any triggers like certain foods?'\n\n"
     "After gathering sufficient information (3-4 exchanges), provide your final response strictly in the following JSON format only, with no extra text:\n\n"
     "{{\n"
     '  "symptoms": "[List user\'s reported symptoms]",\n'
     '  "potential_cause": "[List possible causes based on symptoms]",\n'
     '  "recommended_remedy": "[Provide appropriate self-care advice or recommend professional care]",\n'
     '  "consultation_advice": "[Indicate whether the condition likely requires medical attention or can be managed at home]"\n'
     "}}"
    ),
    ("human", "{history}\nUser: {input}"),
])



def get_medical_response(hid, user_query):
    # Retrieve previous history
    chat_history, created = ChatHistory.objects.get_or_create(hid=hid)
    history = "\n".join(
        [f"User: {q}\nBot: {r}" for q, r in chat_history.conversation.items()]
    )

    # Invoke the model
    chain = prompt | llm
    response_message = chain.invoke({"history": history, "input": user_query})

    # ✅ Extract text correctly
    response_text = response_message.content  # Extract text properly

    # Update conversation history
    chat_history.conversation[user_query] = response_text
    chat_history.save()

    return response_text  # ✅ Return the corrected response

def extract_disease_from_response(response_text):
    """Uses ChatGroq to extract the diagnosed disease from the chatbot's response."""
    
    prompt = f"""
    Given the following medical chatbot response, extract the diagnosed disease or condition. 
    If no disease is mentioned, return 'Unknown'. 
    Response:
    {response_text}
    Answer in this JSON format:
    {{"disease": "extracted disease"}}
    """

    result = llm.predict(prompt)
    
    # Parse JSON output
    try:
        extracted_data = json.loads(result)
        return extracted_data.get("disease", "Unknown")
    except json.JSONDecodeError:
        return "Unknown"

def get_nearby_hospitals(disease, location):
    """Fetches hospitals specialized in treating the given disease at the specified location."""
    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    query = f"{disease} specialist hospital near {location}"
    params = {
        "query": query,
        "key": GOOGLE_PLACES_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "results" in data:
        hospitals = [
            {
                "name": place["name"],
                "address": place["formatted_address"],
                "rating": place.get("rating", "No rating")
            }
            for place in data["results"]
        ]
        return hospitals
    return []