# Multiagent Chatbot

A multi-agent chatbot system built with the Agno framework that provides intelligent calendar management and comprehensive assistance with company tools and processes. The system leverages specialized AI agents working together with a granular permission system for secure and controlled calendar access.

## Features

- **Intelligent Calendar Management**: Schedule, view, update, and delete calendar events with natural language commands
- **Granular Permission System**: Three-tier calendar permission system (Read-only, Read & Update, Full Access)
- **Company Tools Assistant**: Expert guidance on GitHub, VSCode, Jira, Discord, and other development tools
- **Multi-Agent Architecture**: Specialized agents working together for optimal task handling
- **Content Verification**: Built-in quality assurance to ensure accurate and appropriate responses
- **User Authentication**: Secure JWT-based authentication with Google Calendar OAuth
- **Web Search Integration**: Real-time information retrieval using Tavily API
- **Knowledge Base Search**: RAG-powered search for company documentation
- **Multiple Interfaces**: Both web UI (Streamlit) and REST API (FastAPI) available
- **Conversation History**: Persistent storage of agent sessions for context-aware responses

## Project Structure

```
multiagent-chatbot/
├── agents_main.py          # Core multi-agent system implementation
├── api.py                  # FastAPI REST endpoints with authentication
├── app.py                  # Streamlit web interface with permission UI
├── db_functions.py         # Database utility functions
├── tools/                  # Agent tools and utilities
│   ├── calendar_tools.py   # Calendar integration functions
│   └── rag_tool.py         # Knowledge base search tools
├── prompts/                # System prompts for each agent
│   ├── calendar.py         # Calendar agent prompts
│   ├── helper.py           # Helper agent prompts
│   ├── identifier.py       # Request classifier prompts
│   └── revisor.py          # Verification agent prompts
├── tokens/                 # Google Calendar API tokens (permission-specific)
├── data/                   # Documents for RAG knowledge base
├── tmp/                    # Temporary files and agent storage
├── usuarios.sqlite         # User database
├── credentials.json        # Google Calendar API credentials
├── .env                    # Environment variables
├── .env.example            # Environment variables template
└── requirements.txt        # Project dependencies
```

## Prerequisites

- **Python**: 3.8 or higher
- **Google Calendar API**: Valid credentials and OAuth setup
- **API Keys**: At least one of the following:
  - OpenAI API key (for GPT-4o access)
  - Groq API key
- **Tavily API**: For web search functionality
- **SQLite Database**: User information storage

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/multiagent-chatbot.git
cd multiagent-chatbot
```

### 2. Python Environment Setup

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment Configuration

Create your environment configuration:

```bash
cp .env.example .env
```

Edit `.env` file with your API keys:

```env
# Required: OpenAI API configuration
OPENAI_API_KEY=your_openai_api_key

# Alternative LLM providers
GROQ_API_KEY=your_groq_api_key

# Web search
TAVILY_API_KEY=your_tavily_api_key

# Optional: HuggingFace for embeddings
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
```

### 5. Google Calendar API Setup

#### 5.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

#### 5.2 Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Configure consent screen if prompted
4. Select "Desktop application" as application type
5. Download the credentials JSON file
6. Save it as `credentials.json` in the project root

#### 5.3 Configure Example Credentials

Copy the example credentials file and configure:

```bash
cp credentials.example.json credentials.json
```

Edit `credentials.json` with your actual OAuth credentials.

### 6. Database Initialization

Initialize the SQLite database with user information:

```bash
sqlite3 usuarios.sqlite
```

Create the users table:

```sql
CREATE TABLE usuarios (
    username TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    nome TEXT NOT NULL
);

-- Add sample users (optional)
INSERT INTO usuarios (username, email, nome) VALUES
('john', 'john.doe@company.com', 'John'),
('jane', 'jane.smith@company.com', 'Jane');

.quit
```

## Calendar Permission System

The application features a sophisticated three-tier permission system that provides granular control over calendar access while maintaining security best practices.

### Permission Levels

#### 🔍 Read-Only Access
**Scope**: `https://www.googleapis.com/auth/calendar.readonly`

**Capabilities:**
- ✅ View calendar events
- ✅ Search events by date and participants
- ✅ Get calendar information

**Restrictions:**
- ❌ Cannot create new events
- ❌ Cannot edit existing events
- ❌ Cannot delete events

**Use Case**: Perfect for users who only need schedule information without modification capabilities.

#### 📝 Read & Update Access
**Scope**: `https://www.googleapis.com/auth/calendar.events`

**Capabilities:**
- ✅ All read-only capabilities
- ✅ Edit existing calendar events
- ✅ Update event details (time, location, description)
- ✅ Modify participant lists for existing events

**Restrictions:**
- ❌ Cannot create new events
- ❌ Cannot delete events

**Use Case**: Ideal for users who need to manage existing meetings but don't want the chatbot creating or deleting events.

#### 🔧 Full Access (Default)
**Scope**: `https://www.googleapis.com/auth/calendar`

**Capabilities:**
- ✅ Complete calendar control
- ✅ All read and update capabilities
- ✅ Create new calendar events
- ✅ Schedule meetings with participants
- ✅ Delete calendar events
- ✅ Manage secondary calendars

**Restrictions:**
- ✅ No restrictions

**Use Case**: For power users and administrators who need complete calendar management capabilities.

### Permission Selection

1. **During Login**: Choose your desired permission level from the dropdown menu
2. **Permission Details**: Click the expandable "Detalhes da Permissão" section to see capabilities
3. **Change Permissions**: Use the "🔧 Alterar Permissões" button in the sidebar to modify access

### Security Features

- **Separate Authentication**: Each permission level requires separate Google OAuth consent
- **Token Isolation**: Different permission levels use separate authentication tokens stored in `tokens/` directory
- **Agent Awareness**: AI agents are informed of user permissions and will decline unauthorized requests
- **Real-time Validation**: Both frontend and backend validate permissions before executing operations

## Running the Application

### Web Interface (Streamlit)

Launch the interactive web interface:

```bash
streamlit run app.py
```

- Access the interface at `http://localhost:8501`
- Features user-friendly chat interface with permission management
- Real-time responses with agent reasoning display
- Calendar permission status monitoring

### REST API (FastAPI)

Start the API server:

```bash
uvicorn api:app --reload
```

- API available at `http://localhost:8000`
- Interactive documentation at `http://localhost:8000/docs`
- JWT-based authentication with calendar permission support

## Agent System Architecture

The system employs a multi-agent architecture with specialized roles and permission awareness:

### 1. Request Identifier Agent
- **Purpose**: Classifies incoming user requests
- **Output**: Determines if request is for "Calendar", "Helper", or general response
- **Model**: GPT-4o via OpenAI API

### 2. Helper Agent
- **Purpose**: Answers questions about company tools and processes
- **Tools**: Web search (Tavily), RAG search for knowledge base
- **Capabilities**: GitHub, VSCode, Jira, Discord expertise
- **Features**: Conversation history, tool call visibility

### 3. Calendar Auxiliary Agent
- **Purpose**: Resolves user email addresses for calendar invitations
- **Tools**: User email lookup from database
- **Output**: Participant email list or error message

### 4. Calendar Agent
- **Purpose**: Manages all calendar operations with permission awareness
- **Tools**: 
  - Get calendar events
  - Create calendar events (if authorized)
  - Edit calendar events (if authorized)
  - Delete calendar events (if authorized)
  - Time calculations and parsing
- **Features**: Context-aware scheduling, conflict detection, permission validation

### 5. Verifier Agent
- **Purpose**: Quality assurance for all responses
- **Function**: Validates content against company guidelines
- **Output**: Approves, revises, or rejects responses

## Available Tools & Capabilities

### Calendar Tools
- `get_calendar_events`: Retrieve events for specified date ranges
- `create_calendar_event`: Create new calendar events with participants (requires create permission)
- `edit_calendar_event`: Modify existing calendar events (requires update permission)
- `delete_calendar_event`: Remove calendar events (requires delete permission)
- `current_time_tool`: Get current date and time
- `time_delta_tool`: Calculate time offsets (e.g., "tomorrow", "next week")
- `specific_time_tool`: Parse specific time expressions

### User Management Tools
- `get_user_email`: Look up user email addresses from database

### Search Tools
- `TavilyTools`: Real-time web search for current information
- `search_knowledge_base`: RAG-powered search for company documentation

## Usage Examples

### Calendar Operations

```
User: "Schedule a meeting with john.doe tomorrow at 2pm about project review"
Bot: [Creates calendar event with proper time, invites participant - Full Access required]

User: "What meetings do I have this week?"
Bot: [Lists all calendar events for the current week - Available with all permission levels]

User: "Move my 3pm meeting to 4pm tomorrow"
Bot: [Edits existing calendar event - Read & Update permission required]
```

### Help & Support

```
User: "How do I merge a pull request in GitHub?"
Bot: [Provides detailed GitHub PR merging instructions using web search]

User: "What's the shortcut for commenting code in VSCode?"
Bot: [Lists VSCode commenting shortcuts for different languages]

User: "How do I create a Jira ticket?"
Bot: [Explains Jira ticket creation process, may search knowledge base]
```

## Development & Debugging

### Environment Variables

The application supports multiple LLM providers through environment configuration:

```env
# Primary LLM provider (OpenAI)
OPENAI_API_KEY=your_openai_key

# Alternative providers
GROQ_API_KEY=your_groq_key

# Search and tools
TAVILY_API_KEY=your_tavily_key
HUGGINGFACEHUB_API_TOKEN=your_hf_token
```

### Database Management

View and manage users:

```bash
sqlite3 usuarios.sqlite "SELECT * FROM usuarios;"
```

Add new users:

```bash
sqlite3 usuarios.sqlite "INSERT INTO usuarios VALUES ('username', 'email@company.com', 'Full Name');"
```

### Agent Storage

Agent conversations are stored in `tmp/data.db` with SQLite for persistence across sessions.

## Troubleshooting

### Common Issues

1. **Calendar Authentication Failed**
   - Delete permission-specific tokens in `tokens/` directory
   - Verify `credentials.json` is properly configured
   - Check Google Cloud project has Calendar API enabled

2. **Permission Denied Errors**
   - Check selected permission level matches required operation
   - Use "🔧 Alterar Permissões" to change access level
   - Re-authenticate after permission changes

3. **Agent Not Responding**
   - Verify API keys in `.env` file
   - Check internet connection for API calls
   - Ensure OpenAI API key is valid and has sufficient credits

4. **User Email Not Found**
   - Verify user exists in `usuarios.sqlite` database
   - Check username spelling matches database entry

5. **Time Zone Issues**
   - Calendar tools use "America/Sao_Paulo" timezone by default
   - Modify timezone in `tools/calendar_tools.py` if needed

### API Limits

- **Google Calendar**: 1,000,000 quota units per day
- **Tavily**: Depends on your subscription plan
- **OpenAI API**: Based on your API plan and rate limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different permission levels
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
