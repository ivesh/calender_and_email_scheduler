# Lenny Lang - LangChain Framework Agents

## Overview

Lenny Lang is a collection of intelligent agents built using the **LangChain** framework, demonstrating various LangChain Expression Language (LCEL) techniques and patterns. It showcases language translation and weather information retrieval with advanced features like guardrails and tool calling.

## Key Features

### 🔗 LangChain LCEL Techniques
- **Message-based chains**: SystemMessage + HumanMessage patterns
- **Output parsers**: StrOutputParser for clean responses
- **Chain composition**: Model | Parser | Prompt patterns
- **Template-based prompts**: ChatPromptTemplate for reusable prompts
- **Tool calling agents**: AgentExecutor with custom tools

### 🤖 Available Agents

#### 1. Language Translation Agent
Advanced translation system with multiple chain strategies.

#### 2. Weather Information Agent
Real-time weather data with intelligent guardrails.

## Architecture

### Language Translation Agent

#### Core Components (`language_agent/language_expert.py`)

**Model**: ChatGroq with Gemma2-9b-it
**Framework**: LangChain LCEL
**UI**: Streamlit

#### Four Translation Strategies

1. **Basic Message Chain**
   ```python
   messages = [SystemMessage(...), HumanMessage(...)]
   result = model.invoke(messages)
   ```

2. **With Output Parser**
   ```python
   messages = [SystemMessage(...), HumanMessage(...)]
   result = model.invoke(messages)
   result = parser.invoke(result)
   ```

3. **Chained Model + Parser**
   ```python
   chain = model | parser
   result = chain.invoke(messages)
   ```

4. **Full Template Chain**
   ```python
   prompt = ChatPromptTemplate.from_messages([...])
   chain = prompt | model | parser
   result = chain.invoke({"language": lang, "text": text})
   ```

#### Features
- Multi-language translation support
- Interactive Streamlit UI
- Four different LCEL implementation patterns
- Real-time translation

### Weather Information Agent

#### Core Components (`weather_agent/weather_agent.py`)

**Model**: ChatGroq with Qwen3-32b (optimized for tool use)
**Framework**: LangChain with Tool Calling
**API**: OpenWeatherMap
**UI**: Streamlit

#### Architecture Layers

1. **Guardrail Layer**
   - Validates query relevance to weather
   - Prevents off-topic queries
   - Returns YES/NO classification

2. **Agent Layer**
   - Tool calling agent with Weather tool
   - Automatic city extraction
   - Real-time weather data fetching

3. **Tool Layer**
   - OpenWeatherMapAPIWrapper integration
   - Structured weather data retrieval

#### Workflow
```
User Query → Guardrail Check → Agent (if allowed) → Weather Tool → Response
                    ↓
              Blocked (if not weather-related)
```

## Tool Specifications

### Language Translation

#### `behaviour_llm`
```python
behaviour_llm(
    model: ChatGroq,
    choice: int,  # 1-4 for different LCEL patterns
    language: str,  # Target language
    text: str  # Text to translate
) -> str
```

**Choices**:
- `1`: Basic message invocation
- `2`: With output parser
- `3`: Chained model + parser
- `4`: Template-based chain

### Weather Information

#### `check_guardrails`
```python
check_guardrails(
    query: str,
    llm: ChatGroq
) -> bool
```
Returns `True` if query is weather-related, `False` otherwise.

#### `create_weather_agent`
```python
create_weather_agent(
    llm: ChatGroq
) -> AgentExecutor
```
Returns configured agent executor with Weather tool.

#### Weather Tool
```python
Tool(
    name="Weather",
    func=weather_wrapper.run,
    description="Fetch current weather. Input: city name (e.g., London,GB)"
)
```

## Usage Examples

### Language Translation

**Streamlit UI**:
1. Enter target language (e.g., "French", "Spanish")
2. Enter text to translate
3. Select LCEL technique (1-4)
4. Get translated result

**Example**:
- Language: "French"
- Text: "Hello, how are you?"
- Choice: 4 (Template-based)
- Result: "Bonjour, comment allez-vous?"

### Weather Information

**Streamlit UI**:
1. Enter weather query
2. Guardrail validates relevance
3. If allowed, agent fetches weather data
4. Display formatted weather information

**Example Queries**:
- ✅ "What's the weather in London?"
- ✅ "Temperature in New York?"
- ✅ "Is it raining in Tokyo?"
- ❌ "What is 2+2?" (Blocked by guardrail)
- ❌ "Tell me a joke" (Blocked by guardrail)

## Setup Instructions

### Prerequisites
- Python 3.10+
- Groq API key
- OpenWeatherMap API key (for weather agent)

### Installation

1. **Install dependencies**:
```bash
pip install langchain langchain-groq langchain-community streamlit python-dotenv
```

2. **Set up environment variables**:
Create `.env` file:
```
GROQ_API_KEY=your_groq_api_key
OPENWEATHERMAP_API_KEY=your_openweathermap_key
```

3. **Run Language Translation Agent**:
```bash
streamlit run app/lenny_lang/language_agent/language_expert.py
```

4. **Run Weather Agent**:
```bash
streamlit run app/lenny_lang/weather_agent/weather_agent.py
```

## Configuration

### Model Selection

**Language Agent**:
```python
model = ChatGroq(
    model="gemma2-9b-it",
    groq_api_key=groq_api_key
)
```

**Weather Agent**:
```python
llm = ChatGroq(
    model="qwen/qwen3-32b",  # Optimized for tool calling
    groq_api_key=groq_api_key,
    temperature=0  # Deterministic for tool use
)
```

### Guardrail Customization

Modify guardrail prompt in `weather_agent.py`:
```python
system_instruction = """
You are a strict guardrail agent.
Your ONLY job is to classify if the user's input is about weather.
- If YES, reply: YES
- If NO, reply: NO
"""
```

## Technical Details

### LangChain LCEL Patterns

#### Pattern 1: Direct Invocation
```python
result = model.invoke(messages)
```
- Simplest approach
- Returns AIMessage object
- Requires manual parsing

#### Pattern 2: With Parser
```python
result = model.invoke(messages)
result = parser.invoke(result)
```
- Adds output parsing step
- Returns clean string
- Two-step process

#### Pattern 3: Chained
```python
chain = model | parser
result = chain.invoke(messages)
```
- Pipes model to parser
- Single invocation
- More elegant

#### Pattern 4: Template-based
```python
prompt = ChatPromptTemplate.from_messages([...])
chain = prompt | model | parser
result = chain.invoke({"language": lang, "text": text})
```
- Reusable prompt templates
- Variable substitution
- Most flexible and maintainable

### Tool Calling Agent

**Components**:
1. **Tool Definition**: Wraps OpenWeatherMap API
2. **Prompt**: Instructs agent on tool usage
3. **Agent**: create_tool_calling_agent with LLM + tools
4. **Executor**: AgentExecutor runs the agent loop

**Flow**:
```
Input → Agent analyzes → Decides to use tool → Tool execution → Response
```

### Guardrail Implementation

**Purpose**: Prevent off-topic queries and API waste

**Mechanism**:
1. Pre-process query with classification LLM
2. Check for "YES" in response
3. Allow/block based on classification

**Benefits**:
- Reduces API costs
- Improves user experience
- Prevents misuse

## Integration Points

### With Unified Application
Both agents can be exposed via REST API:
```python
@app.post("/api/lenny/translate")
async def translate(language: str, text: str, choice: int):
    # Invoke language agent
    
@app.post("/api/lenny/weather")
async def weather(query: str):
    # Invoke weather agent with guardrails
```

### Streamlit UI Integration
Can be embedded in larger dashboard or run standalone.

## Observability

### Logging
- Model invocations
- Chain execution steps
- Tool calls
- Guardrail decisions

### Metrics to Track
- Translation request count
- Weather query success rate
- Guardrail block rate
- Average response time
- API usage per model

## Best Practices

### Language Translation
- Use template-based chains (choice 4) for production
- Cache common translations
- Validate target language
- Handle translation errors gracefully

### Weather Agent
- Always use guardrails to prevent API waste
- Set temperature=0 for tool calling
- Use models optimized for tool use (Qwen, Llama3)
- Provide clear tool descriptions

### LangChain LCEL
- Prefer chains over manual invocations
- Use templates for reusability
- Leverage output parsers
- Keep chains simple and composable

## Limitations

- **API Dependencies**: Requires Groq and OpenWeatherMap APIs
- **Rate Limits**: Subject to API quotas
- **Language Support**: Limited by underlying model capabilities
- **Weather Data**: Current weather only, no forecasts
- **Guardrail Accuracy**: May occasionally misclassify edge cases

## Future Enhancements

- [ ] Add more language pairs
- [ ] Implement translation caching
- [ ] Extend weather to forecasts
- [ ] Add more guardrail categories
- [ ] Implement conversation memory
- [ ] Add batch translation support
- [ ] Create unified Streamlit dashboard
- [ ] Add evaluation metrics

## Troubleshooting

### API Key Issues
```bash
# Verify .env file exists and contains keys
cat .env | grep GROQ_API_KEY
cat .env | grep OPENWEATHERMAP_API_KEY
```

### Streamlit Not Starting
```bash
# Install Streamlit
pip install streamlit

# Check Python version
python --version  # Should be 3.10+
```

### Guardrail Always Blocking
- Check guardrail prompt
- Verify LLM is responding correctly
- Test with explicit weather queries

### Translation Errors
- Verify Groq API key is valid
- Check model availability
- Review error logs in Streamlit

## References

- [LangChain Documentation](https://python.langchain.com/)
- [LangChain LCEL Guide](https://python.langchain.com/docs/expression_language/)
- [Groq API](https://groq.com/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Streamlit Documentation](https://docs.streamlit.io/)
