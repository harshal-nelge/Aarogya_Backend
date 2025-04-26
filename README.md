# AAROGYA - Centralized Healthcare System with Virtual Health Card

Aarogya Lakshya is an intelligent healthcare platform leveraging AI to provide personalized medical assistance, disease diagnosis, and healthcare resource connectivity.

## 🌟 Features

- **AI-Powered Medical Assistant**: Conversational medical chatbot powered by advanced LLMs (Llama 3.3 70B) and memory integration using Sqlite3 database
- **Disease Diagnosis**: Intelligent symptom analysis and diagnosis suggestions
- **Medical Report Analysis**: Upload and analyze medical reports using Google Gemini AI
- **Hospital Finder**: Locate specialized healthcare facilities based on diagnosed conditions
- **Disease Outbreak Monitoring**: Track and visualize disease outbreaks across regions
- **Health Content Aggregation**: Curated educational resources, videos, and articles
- **Local Health News**: Region-specific health alerts and news 

## 🛠️ Technology Stack

- **Backend Framework**: Django + Django REST Framework
- **AI & ML**:
  - Google Gemini AI (medical report analysis)
  - Groq LLM API (medical chatbot)
  - Google Places API (hospital search)
- **Data Processing**: 
  - BeautifulSoup (web scraping)
  - PyPDF2 (PDF processing)
- **Storage**: Google Cloud Storage
- **APIs**:
  - YouTube Data API (health videos)
  - Google Custom Search (health articles)
  - Event Registry API (health news)

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Django 5.1+
- Required API keys:
  - GROQ_API_KEY
  - GEMINI_API_KEY
  - GOOGLE_PLACES_API_KEY
  - YOUTUBE_API_KEY
  - EVENT_REGISTRY_API_KEY
  - Google Cloud Storage credentials

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aarogya-lakshya.git
   cd aarogya-lakshya
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   GOOGLE_PLACES_API_KEY=your_google_places_api_key
   YOUTUBE_API_KEY=your_youtube_api_key
   EVENT_REGISTRY_API_KEY=your_event_registry_api_key
   SEARCH_ENGINE_ID=your_google_cse_id
   BUCKET_NAME=your_gcs_bucket_name
   ```

4. Place your Google Cloud Storage service account key in `card/service-account-key.json`

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat/` | POST | Interact with the medical chatbot |
| `/api/upload-report/` | POST | Upload and analyze medical reports |
| `/api/get-hospitals/` | POST | Find specialized hospitals nearby |
| `/api/get-news/` | POST | Get local health news |
| `/api/get-outbreaks/` | POST | Get disease outbreak data |
| `/api/get-content/` | POST | Get educational content for diagnosed conditions |

## 📋 API Usage Examples

### Medical Chat

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"hid": "patient123", "query": "I have a severe headache and fever"}'
```

### Upload Medical Report

```bash
curl -X POST http://localhost:8000/api/upload-report/ \
  -F "document=@path/to/report.pdf"
```

### Find Hospitals

```bash
curl -X POST http://localhost:8000/api/get-hospitals/ \
  -H "Content-Type: application/json" \
  -d '{"hid": "patient123", "location": "New Delhi"}'
```

### Get Health News

```bash
curl -X POST http://localhost:8000/api/get-news/ \
  -H "Content-Type: application/json" \
  -d '{"city": "Mumbai", "country": "India"}'
```

### Get Disease Outbreaks

```bash
curl -X POST http://localhost:8000/api/get-outbreaks/ \
  -H "Content-Type: application/json" \
  -d '{"year": 2024, "week": 15}'
```

### Get Educational Content

```bash
curl -X POST http://localhost:8000/api/get-content/ \
  -H "Content-Type: application/json" \
  -d '{"hid": "patient123"}'
```

## 🧠 How It Works

1. **Patient Interaction**: Users interact with the AI medical assistant through natural language
2. **Symptom Analysis**: The system analyzes symptoms through a conversational interface
3. **Diagnosis**: AI identifies potential causes and recommends next steps
4. **Resource Connection**: Based on the diagnosis, the system connects users with:
   - Specialized healthcare facilities
   - Educational videos and articles
   - Local health alerts
5. **Report Analysis**: Users can upload medical reports for AI-powered summary and interpretation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🌐 Security Note

This application handles sensitive medical information. In a production environment, ensure:
- Proper authentication and authorization
- Secure storage of API keys
- HIPAA compliance (if applicable)
- Data encryption at rest and in transit
