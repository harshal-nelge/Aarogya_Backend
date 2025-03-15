from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from .models import ChatHistory
from dotenv import load_dotenv
import os

load_dotenv()

# Get API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    max_tokens=500,
    timeout=10,
    max_retries=2,
)

# Chat Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", 
         "You are a conversational medical chatbot. Provide diagnosis and recommendations based on the user's symptoms. "
         "If the symptoms seem severe, advise them to consult a doctor. Keep your responses short and conversational.\n\n"
         "Engage with the user by asking relevant follow-up questions based on their symptoms. "
         "For example:\n"
         "- If the user mentions fever, ask: 'How many days have you had a fever?'\n"
         "- If the user reports chest pain, ask: 'Do you also feel shortness of breath or dizziness?'\n"
         "- If the user has a headache, ask: 'Is it a throbbing pain or more like pressure?'\n"
         "- If the user mentions stomach pain, ask: 'Is the pain constant, or does it come and go?'\n"
         "Use natural language to make the conversation feel smooth and helpful and try to end the chat after 3 to 4 conversations."),
        ("human", "{history}\nUser: {input}"),
    ]
)

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
