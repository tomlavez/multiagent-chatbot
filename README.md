# Multi-Agent Chatbot

A multi-agent chatbot system that integrates calendar functionality, web search, and knowledge base using OpenAI API.

## Features

- **Multi-Agent System**: Different specialized agents for specific tasks
- **Google Calendar Integration**: Create, edit, view, and delete events
- **Web Search**: Real-time Tavily integration
- **Knowledge Base**: RAG system for document queries
- **Web Interface**: Intuitive Streamlit interface
- **REST API**: FastAPI for integration with other systems
- **Permission System**: Granular calendar access control
- **Authentication**: User login and registration system

## Project Structure

```
multiagent-chatbot/
├── src/                          # Main source code
│   ├── agents/                   # Agents and prompts
│   │   ├── prompts/             # Agent prompts
│   │   └── agents_main.py       # Main agent logic
│   ├── api/                     # FastAPI
│   │   ├── api.py              # API endpoints
│   │   └── db_functions.py     # Database functions
│   ├── tools/                   # Agent tools
│   │   ├── calendar_tools.py   # Calendar tools
│   │   └── rag_tool.py         # RAG search tool
│   └── web/                     # Web interface
│       └── app.py              # Streamlit application
├── config/                      # Configuration files
│   ├── .env                    # Environment variables
│   ├── .env.example           # Environment variables template
│   ├── credentials.json       # Google credentials
│   └── credentials.example.json
├── auth/                        # Authentication files
│   ├── token.json             # Main Google token
│   └── tokens/                # User-specific tokens
├── database/                    # Database files
│   ├── usuarios.sqlite        # User database
│   └── tmp/                   # Agent temporary data
├── data/                        # Documents for RAG
├── docs/                        # Documentation
├── run_api.py                   # Script to run the API
├── run_web.py                   # Script to run the web interface
└── requirements.txt             # Python dependencies
```

## Prerequisites

- Python 3.8+
- Google account with Google Calendar API access
- OpenAI API key
- Tavily API key (optional, for web search)
- HuggingFace token (optional, for RAG)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/tomlavez/multiagent-chatbot.git
cd multiagent-chatbot
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp config/.env.example config/.env
```

Edit the `config/.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_key_here
TAVILY_API_KEY=your_tavily_key_here
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
```

5. Configure Google Calendar credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project or select an existing one
   - Enable the Google Calendar API
   - Create OAuth 2.0 credentials
   - Download the JSON file and save as `config/credentials.json`

## Usage

### Run the API (FastAPI)

```bash
python run_api.py
```

The API will be available at `http://localhost:8000`

### Run the Web Interface (Streamlit)

```bash
python run_web.py
```

The web interface will be available at `http://localhost:8501`

### Using the API directly

1. **User registration:**
```bash
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "password": "password", "email": "email@example.com"}'
```

2. **Login:**
```bash
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "password": "password", "calendar_permissions": "full_access"}'
```

3. **Chat:**
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -H "token: YOUR_TOKEN_HERE" \
     -d '{"message": "Create an event for tomorrow at 2pm", "username": "user"}'
```

## Calendar Permission Levels

- **readonly**: View events only
- **read_update**: View and edit existing events
- **full_access**: Full control (create, edit, delete events)

## Available Agents

1. **Identifier Agent**: Classifies the type of user request
2. **Helper Agent**: Answers general questions and performs searches
3. **Calendar Agent**: Manages Google Calendar events
4. **Auxiliary Agent**: Searches user information
5. **Verifier Agent**: Validates and reviews responses

## Integrated Tools

- **Google Calendar**: Complete event management
- **Tavily Search**: Real-time web search
- **RAG System**: Local knowledge base queries
- **Time System**: Date and time manipulation tools

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
