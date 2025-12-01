# Jarvis ADK - Google ADK Framework Agent

## Overview

Jarvis ADK is a comprehensive voice-enabled AI assistant built using the **Google Agent Development Kit (ADK)** and powered by **Gemini 2.0 Flash Experimental**. It provides intelligent calendar management, trip planning, and email functionality through natural language interactions.

## Key Features

### 🎯 Multi-Modal Interaction
- **Voice Input**: Native audio processing with Gemini 2.0 Flash
- **Text Input**: Traditional text-based interactions
- **Real-time Streaming**: WebSocket-based streaming for instant responses
- **Voice Output**: Natural voice responses with customizable voice profiles (Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, Zephyr)

### 🛠️ Agent Capabilities

#### Calendar Management Tools
- **`list_events`**: Retrieve calendar events for specified time periods
- **`create_event`**: Add new events to Google Calendar
- **`edit_event`**: Modify existing calendar events
- **`delete_event`**: Remove events from calendar
- **`find_free_time`**: Discover available time slots

#### Advanced Tools
- **`plan_trip`**: AI-powered trip planning using CrewAI integration
- **`send_email`**: Email composition and sending functionality

## Architecture

### Core Components

#### 1. Agent Definition (`agent.py`)
The brain of the system, defining:
- **Model**: Gemini 2.0 Flash Experimental
- **Instructions**: Detailed behavioral guidelines
- **Tools**: Registered calendar and utility functions
- **Personality**: Jarvis - helpful, concise, proactive

#### 2. Tools Layer (`tools/`)
Implements the actual functionality:
- **Calendar Tools**: Integration with Google Calendar API
- **Trip Planner**: Delegates to CrewAI trip planning crew
- **Email Tool**: Email sending capabilities
- **Utility Functions**: Time handling, formatting, etc.

#### 3. Calendar Integration (`calendar/`)
- **Authentication**: OAuth 2.0 flow with Google Calendar API
- **Event Operations**: CRUD operations for calendar events
- **Time Management**: Timezone-aware date/time handling
- **Calendar Utils**: Helper functions for date formatting and current time

### Session Management

Uses **InMemorySessionService** for:
- User session tracking
- Conversation history
- State persistence across interactions
- Multi-user support with session IDs

### Streaming Architecture

```
Client (Browser) <--WebSocket--> FastAPI Server <--> ADK Runner <--> Gemini 2.0
                                                           |
                                                      LiveRequestQueue
                                                           |
                                                    Tools (Calendar, etc.)
```

## Tool Specifications

### Calendar Tools

#### `list_events`
```python
list_events(
    calendar_id: str = "primary",
    start_date: str = "",  # YYYY-MM-DD or empty for today
    days: int = 1,
    max_results: int = 100
) -> str
```
Returns formatted list of calendar events.

#### `create_event`
```python
create_event(
    calendar_id: str = "primary",
    summary: str,  # Event title
    start_time: str,  # YYYY-MM-DD HH:MM
    end_time: str,  # YYYY-MM-DD HH:MM
    description: str = "",
    location: str = ""
) -> str
```
Creates a new calendar event.

#### `edit_event`
```python
edit_event(
    calendar_id: str = "primary",
    event_id: str,  # From list_events
    summary: str = "",  # Empty to keep unchanged
    start_time: str = "",  # Empty to keep unchanged
    end_time: str = ""  # Empty to keep unchanged
) -> str
```
Modifies an existing event.

#### `delete_event`
```python
delete_event(
    calendar_id: str = "primary",
    event_id: str
) -> str
```
Removes an event from the calendar.

### Advanced Tools

#### `plan_trip`
```python
plan_trip(
    origin: str,
    cities: str,
    date_range: str,
    interests: str
) -> str
```
Generates comprehensive trip itinerary using CrewAI agents.

#### `send_email`
```python
send_email(
    to: str,
    subject: str,
    body: str
) -> str
```
Sends an email to specified recipient.

## Usage Examples

### Voice Interactions
- "What's on my calendar today?"
- "Schedule a meeting with John tomorrow at 2 PM"
- "Move my 3 PM meeting to 4 PM"
- "Delete my dentist appointment"
- "Plan a trip to Paris and Rome next month"

### Text Interactions
Same natural language queries work via text input.

## Setup Instructions

### Prerequisites
- Python 3.10+
- Google Cloud Project with Calendar API enabled
- Gemini API key
- OAuth 2.0 credentials (`credentials.json`)

### Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**:
Create `.env` file:
```
GOOGLE_API_KEY=your_gemini_api_key
```

3. **Configure Google Calendar**:
```bash
python setup_calendar_auth.py
```

4. **Run the agent**:
```bash
# Quick test with ADK web interface
adk web

# Full application with custom UI
uvicorn app.main:app --reload
```

## Configuration

### Voice Configuration
Customize voice in `main.py`:
```python
speech_config = types.SpeechConfig(
    voice_config=types.VoiceConfig(
        prebuilt_voice_config=types.PrebuiltVoiceConfig(
            voice_name="Puck"  # Change to preferred voice
        )
    )
)
```

### Response Modality
Toggle between text and audio:
```python
modality = "AUDIO"  # or "TEXT"
config = {"response_modalities": [modality]}
```

## Technical Details

### Model Selection
**Gemini 2.0 Flash Experimental** chosen for:
- Native audio understanding
- Fast real-time responses
- Superior tool calling capabilities
- Multi-modal processing (text + audio)

### WebSocket Protocol
- **Connection**: `/ws/{session_id}?is_audio=true|false`
- **Message Format**: JSON with `mime_type`, `data`, `role`
- **Supported MIME Types**: `text/plain`, `audio/pcm`
- **Streaming**: Partial responses for real-time feel

### Security
- OAuth 2.0 for Google Calendar access
- Secure token storage in user directory
- Environment variable-based API key management
- No hardcoded credentials

## Integration Points

### With Taylor Crew
The `plan_trip` tool delegates to the CrewAI trip planner:
```python
from app.taylor_crew.trip_planner.main import TripCrew
```

### With Email System
Email functionality can integrate with the email crew for advanced workflows.

## Observability

### Logging
Console logging for:
- Client connections/disconnections
- Message flow (client ↔ agent)
- Tool invocations
- Errors and exceptions

### Monitoring Points
- Session creation/destruction
- WebSocket message counts
- Tool execution times
- API call success/failure rates

## Best Practices

### Agent Instructions
The agent is instructed to:
- Be concise and avoid verbosity
- Never show raw tool outputs
- Use context intelligently (default to "today" when appropriate)
- Confirm destructive actions (deletions)
- Format dates consistently (MM-DD-YYYY for display)

### Error Handling
- Graceful degradation on API failures
- User-friendly error messages
- Automatic retry for transient failures
- Detailed logging for debugging

## Limitations

- Calendar API quota limits (check Google Cloud Console)
- Audio streaming requires modern browser with WebSocket support
- Voice recognition quality depends on microphone and environment
- Trip planning requires additional API keys (Serper, Browserless)

## Future Enhancements

- [ ] Multi-calendar support with smart selection
- [ ] Recurring event management
- [ ] Calendar sharing and permissions
- [ ] Integration with other Google Workspace apps
- [ ] Advanced natural language date parsing
- [ ] Proactive meeting suggestions
- [ ] Calendar analytics and insights

## Troubleshooting

### Authentication Issues
```bash
# Delete token and re-authenticate
rm ~/.credentials/calendar_token.json
python setup_calendar_auth.py
```

### WebSocket Connection Failures
- Check firewall settings
- Verify port 8000 is available
- Ensure browser supports WebSockets

### Tool Execution Errors
- Verify API keys in `.env`
- Check Google Calendar API quota
- Review logs for detailed error messages

## References

- [Google ADK Documentation](https://github.com/google/adk)
- [Gemini API](https://ai.google.dev/gemini-api/docs)
- [Google Calendar API](https://developers.google.com/calendar/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
