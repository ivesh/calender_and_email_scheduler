# Taylor Crew - CrewAI Framework Multi-Agent System

## Overview

Taylor Crew is a sophisticated multi-agent system built using the **CrewAI** framework, demonstrating advanced agent orchestration and collaboration. It features two complete crew implementations: a trip planning system and an email automation workflow with LangGraph integration.

## Key Features

### 🤝 Multi-Agent Orchestration
- **Role-based agents**: Specialized agents with distinct responsibilities
- **Sequential workflows**: Tasks executed in logical order
- **Agent collaboration**: Agents share context and build on each other's work
- **Autonomous decision-making**: Agents make intelligent choices within their domain

### 🚀 Available Crews

#### 1. Trip Planner Crew
Multi-agent system for comprehensive travel planning.

#### 2. Email Crew
Automated email processing with LangGraph state management.

## Architecture

### Trip Planner Crew

#### Agents (`trip_planner/trip_agents.py`)

1. **City Selection Agent**
   - **Role**: Expert Travel Agent
   - **Goal**: Select the best city based on criteria
   - **Tools**: Search internet, scrape websites
   - **Backstory**: Specialist in analyzing travel data

2. **Local Expert Agent**
   - **Role**: Local Expert at selected city
   - **Goal**: Provide best insights about the city
   - **Tools**: Search internet, scrape and summarize websites
   - **Backstory**: Knowledgeable local guide

3. **Travel Concierge Agent**
   - **Role**: Amazing Travel Concierge
   - **Goal**: Create detailed itinerary with budget
   - **Tools**: Search internet, calculator
   - **Backstory**: Expert in travel logistics

#### Tasks (`trip_planner/trip_tasks.py`)

1. **Identify Task**
   - Analyze city options
   - Consider weather, season, prices
   - Select best city with justification

2. **Gather Task**
   - Research selected city
   - Find attractions, restaurants, events
   - Compile comprehensive information

3. **Plan Task**
   - Create day-by-day itinerary
   - Include budget breakdown
   - Add packing suggestions
   - Provide practical tips

#### Workflow
```
User Input (origin, cities, dates, interests)
    ↓
City Selector Agent → Identify best city
    ↓
Local Expert Agent → Gather city information
    ↓
Travel Concierge Agent → Create detailed itinerary
    ↓
Complete Trip Plan
```

### Email Crew

#### Architecture (`e_mail_crew/`)

**Framework**: CrewAI + LangGraph
**Integration**: Gmail API
**State Management**: LangGraph StateGraph

#### Components

1. **Graph Definition** (`src/graph.py`)
   - Defines workflow nodes and edges
   - Manages state transitions
   - Orchestrates crew execution

2. **Nodes** (`src/nodes.py`)
   - Individual workflow steps
   - State transformations
   - Crew invocations

3. **State** (`src/state.py`)
   - Shared state across workflow
   - Email data structures
   - Processing status

4. **Crew** (`src/crew/`)
   - **Agents**: Email processing agents
   - **Tasks**: Email analysis and draft creation
   - **Tools**: Gmail draft tool

#### Workflow
```
Check Emails → Analyze Emails → Create Drafts → Save to Gmail
```

## Tool Specifications

### Trip Planner Tools

#### Search Tools (`trip_planner/tools/search_tools.py`)
```python
SearchTools.search_internet(query: str) -> str
```
Searches the internet using Serper API.

#### Browser Tools (`trip_planner/tools/browser_tools.py`)
```python
BrowserTools.scrape_and_summarize_website(url: str) -> str
```
Scrapes and summarizes website content using Browserless.

#### Calculator Tool (`trip_planner/tools/calculator_tools.py`)
```python
CalculatorTools.calculate(expression: str) -> float
```
Performs mathematical calculations for budgeting.

### Email Crew Tools

#### Gmail Draft Tool (`e_mail_crew/src/crew/tools.py`)
```python
GmailDraftTool.create_draft(
    to: str,
    subject: str,
    body: str
) -> str
```
Creates draft email in Gmail.

## Usage Examples

### Trip Planner

**Command Line**:
```bash
cd app/taylor_crew/trip_planner
python main.py
```

**Interactive Prompts**:
```
From where will you be traveling from?
> San Francisco

What are the cities options you are interested in visiting?
> Paris, Rome, Barcelona

What is the date range you are interested in traveling?
> June 15-25, 2024

What are some of your high level interests and hobbies?
> Art, food, history, architecture
```

**Output**:
Comprehensive trip plan including:
- Selected city with justification
- Day-by-day itinerary
- Restaurant recommendations
- Attraction details
- Budget breakdown
- Packing list
- Travel tips

### Email Crew

**Command Line**:
```bash
cd app/taylor_crew/e_mail_crew
python main.py
```

**Automated Process**:
1. Fetches recent emails from Gmail
2. Analyzes email content and priority
3. Generates draft responses
4. Saves drafts to Gmail

## Setup Instructions

### Prerequisites
- Python 3.10+
- OpenAI API key (or other LLM provider)
- Serper API key (for search)
- Browserless API key (for web scraping)
- Google Cloud Project with Gmail API enabled (for email crew)

### Installation

1. **Install dependencies**:
```bash
pip install crewai langchain langgraph google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

2. **Set up environment variables**:
Create `.env` file:
```
OPENAI_API_KEY=your_openai_key
SERPER_API_KEY=your_serper_key
BROWSERLESS_API_KEY=your_browserless_key
```

3. **For Email Crew - Gmail Setup**:
```bash
# Follow Google's instructions to create credentials.json
# Place credentials.json in e_mail_crew/ directory
```

4. **Run Trip Planner**:
```bash
python app/taylor_crew/trip_planner/main.py
```

5. **Run Email Crew**:
```bash
python app/taylor_crew/e_mail_crew/main.py
```

## Configuration

### Model Selection

**Default (GPT-4)**:
```python
# Agents use GPT-4 by default
```

**Custom Model**:
```python
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model='gpt-3.5-turbo')

agent = Agent(
    role='...',
    goal='...',
    backstory='...',
    llm=llm  # Custom LLM
)
```

**Local Models (Ollama)**:
```python
from langchain.llms import Ollama

ollama_model = Ollama(model="llama2")

agent = Agent(
    role='...',
    goal='...',
    backstory='...',
    llm=ollama_model
)
```

### Crew Configuration

```python
crew = Crew(
    agents=[agent1, agent2, agent3],
    tasks=[task1, task2, task3],
    verbose=True,  # Enable detailed logging
    process=Process.sequential  # or Process.hierarchical
)
```

## Technical Details

### CrewAI Framework

**Core Concepts**:
- **Agents**: Autonomous entities with roles and goals
- **Tasks**: Specific objectives assigned to agents
- **Crew**: Orchestrator managing agents and tasks
- **Process**: Sequential or hierarchical execution

**Agent Attributes**:
```python
Agent(
    role="Role description",
    goal="What the agent aims to achieve",
    backstory="Agent's background and expertise",
    tools=[tool1, tool2],  # Available tools
    llm=model,  # Language model
    verbose=True  # Logging
)
```

**Task Attributes**:
```python
Task(
    description="Detailed task description",
    agent=agent,  # Assigned agent
    expected_output="What output should look like"
)
```

### LangGraph Integration

**State Management**:
```python
from langgraph.graph import StateGraph

class EmailState(TypedDict):
    emails: List[Email]
    drafts: List[Draft]
    status: str

graph = StateGraph(EmailState)
graph.add_node("check_emails", check_emails_node)
graph.add_edge("check_emails", "analyze_emails")
```

**Benefits**:
- Explicit state transitions
- Conditional branching
- Error recovery
- Workflow visualization

### Tool Integration

**Custom Tools**:
```python
from langchain.tools import Tool

custom_tool = Tool(
    name="ToolName",
    func=your_function,
    description="What the tool does"
)
```

**API-based Tools**:
- Serper for search
- Browserless for web scraping
- Gmail API for email operations

## Integration Points

### With Jarvis ADK
Trip planner is called from Jarvis via `plan_trip` tool:
```python
from app.taylor_crew.trip_planner.main import TripCrew

def plan_trip(origin, cities, date_range, interests):
    crew = TripCrew(origin, cities, date_range, interests)
    return crew.run()
```

### With Unified Application
Expose crews via REST API:
```python
@app.post("/api/taylor/plan-trip")
async def plan_trip_endpoint(request: TripRequest):
    crew = TripCrew(...)
    return crew.run()

@app.post("/api/taylor/process-emails")
async def process_emails():
    workflow = WorkFlow()
    return workflow.app.invoke({})
```

## Observability

### Logging
CrewAI provides built-in verbose logging:
```
[Agent Name] is working on: Task description
[Agent Name] used tool: Tool name
[Agent Name] completed task
```

### Metrics to Track
- Task completion time per agent
- Tool usage frequency
- Success/failure rates
- Token usage per task
- End-to-end workflow duration

## Best Practices

### Agent Design
- **Clear roles**: Each agent should have distinct responsibility
- **Specific goals**: Well-defined objectives
- **Rich backstory**: Helps model understand context
- **Appropriate tools**: Only tools relevant to role

### Task Design
- **Detailed descriptions**: Clear instructions for agents
- **Expected output**: Specify format and content
- **Logical sequence**: Tasks build on previous results
- **Validation criteria**: How to measure success

### Crew Orchestration
- **Sequential for dependencies**: When tasks depend on previous results
- **Parallel for independence**: When tasks can run concurrently
- **Hierarchical for management**: When one agent manages others

## Limitations

- **API Costs**: Multiple LLM calls can be expensive
- **Execution Time**: Sequential workflows can be slow
- **API Dependencies**: Requires external services (Serper, Browserless)
- **Rate Limits**: Subject to API quotas
- **Determinism**: Agent decisions may vary between runs

## Future Enhancements

- [ ] Add more specialized agents (hotel booking, flight search)
- [ ] Implement parallel task execution where possible
- [ ] Add human-in-the-loop for critical decisions
- [ ] Create agent memory for learning from past trips
- [ ] Implement cost optimization strategies
- [ ] Add real-time progress tracking
- [ ] Create web UI for trip planning
- [ ] Expand email crew to handle more scenarios

## Troubleshooting

### API Key Issues
```bash
# Verify all required keys in .env
cat .env | grep OPENAI_API_KEY
cat .env | grep SERPER_API_KEY
cat .env | grep BROWSERLESS_API_KEY
```

### Crew Execution Failures
- Check agent tool availability
- Verify API quotas not exceeded
- Review verbose logs for errors
- Ensure task descriptions are clear

### Gmail API Issues
- Verify credentials.json is present
- Re-authenticate if token expired
- Check Gmail API is enabled in Google Cloud Console
- Review OAuth scopes

### Slow Execution
- Use faster models (GPT-3.5 instead of GPT-4)
- Reduce number of search queries
- Implement caching for repeated queries
- Consider parallel execution

## References

- [CrewAI Documentation](https://docs.crewai.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Serper API](https://serper.dev/)
- [Browserless](https://www.browserless.io/)
- [Gmail API](https://developers.google.com/gmail/api)
