# MCP (Model Context Protocol) Integration

## Overview

The MCP (Model Context Protocol) integration demonstrates how to extend Google ADK agents with custom server-based tools. MCP provides a standardized way to connect AI models to external data sources and tools through a client-server architecture.

## Key Features

### 🔌 MCP Protocol
- **Standardized interface**: Consistent tool discovery and invocation
- **Server-based tools**: Tools run in separate processes
- **Stdio communication**: Simple process-based communication
- **Tool filtering**: Selective tool loading for security and performance
- **Local and remote servers**: Support for both deployment models

### 🛠️ Available Implementations

#### 1. Local MCP Server
Database operations through MCP protocol.

#### 2. Remote MCP Agent
Connection to external MCP servers.

#### 3. Comparison Demo
Traditional vs MCP-based agent comparison.

## Architecture

### Local MCP Server

#### Components

**Server** (`local_mcp/server.py`)
- SQLite database operations
- MCP protocol implementation
- Tool definitions (list_tables, query, insert, etc.)
- Stdio-based communication

**Agent** (`local_mcp/agent.py`)
- LlmAgent with MCPToolset
- Connects to local server via stdio
- Gemini 2.0 Flash model
- Database query capabilities

**Database** (`local_mcp/create_db.py`)
- Sample SQLite database creation
- Product catalog schema
- Test data population

#### MCP Tools Available

1. **list_tables**: List all database tables
2. **describe_table**: Get table schema
3. **query**: Execute SELECT queries
4. **insert**: Add new records
5. **update**: Modify existing records
6. **delete**: Remove records

#### Architecture Flow
```
ADK Agent → MCPToolset → Stdio → MCP Server → SQLite Database
                                      ↓
                                  Tool Results
                                      ↓
                              ← Response ←
```

### Remote MCP Agent

#### Components

**Agent** (`remote_mcp_agent/agent.py`)
- Connects to external MCP servers
- HTTP/WebSocket communication
- Tool discovery and invocation
- Remote resource access

#### Use Cases
- Connect to cloud-based MCP servers
- Access shared tool repositories
- Integrate with third-party MCP services
- Distributed agent architectures

### Comparison Demo

#### Traditional Agent (`demo_comparison/traditional_agent.py`)
- Direct tool implementation
- Inline function definitions
- No protocol overhead
- Simple but less scalable

#### MCP Agent (`demo_comparison/mcp_agent.py`)
- Protocol-based tool access
- Server-managed tools
- Standardized interface
- More scalable and maintainable

## Tool Specifications

### MCPToolset Configuration

```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="python3",
        args=["/path/to/server.py"]
    ),
    tool_filter=['list_tables', 'query']  # Optional: limit tools
)
```

### Database Tools

#### list_tables
```python
# Returns list of all tables in database
Result: ["products", "customers", "orders"]
```

#### describe_table
```python
# Input: table_name
# Returns: Column definitions
Result: {
    "columns": [
        {"name": "id", "type": "INTEGER"},
        {"name": "name", "type": "TEXT"},
        ...
    ]
}
```

#### query
```python
# Input: sql (SELECT statement)
# Returns: Query results as JSON
Result: [
    {"id": 1, "name": "Product A", "price": 29.99},
    {"id": 2, "name": "Product B", "price": 39.99}
]
```

#### insert
```python
# Input: table_name, data (dict)
# Returns: Success message with inserted ID
```

#### update
```python
# Input: table_name, id, data (dict)
# Returns: Success message
```

#### delete
```python
# Input: table_name, id
# Returns: Success message
```

## Usage Examples

### Local MCP Server

**Setup Database**:
```bash
cd app/mcp/adk-mcp-tutorial/local_mcp
python create_db.py
```

**Run Agent**:
```bash
adk web --agent local_mcp.agent:root_agent
```

**Example Queries**:
- "What tables are in the database?"
- "Show me all products"
- "Find products under $50"
- "Add a new product called 'Widget' for $25"
- "Update product 1 to cost $35"

### Remote MCP Agent

**Configuration**:
```python
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, HttpServerParameters

toolset = MCPToolset(
    connection_params=HttpServerParameters(
        url="https://mcp-server.example.com"
    )
)
```

**Use Cases**:
- Access shared company tools
- Connect to cloud databases
- Integrate with external APIs
- Use managed MCP services

### Comparison Demo

**Run Traditional Agent**:
```bash
adk web --agent demo_comparison.traditional_agent:root_agent
```

**Run MCP Agent**:
```bash
adk web --agent demo_comparison.mcp_agent:root_agent
```

**Compare**:
- Functionality: Same
- Architecture: Different
- Scalability: MCP wins
- Simplicity: Traditional wins

## Setup Instructions

### Prerequisites
- Python 3.10+
- Google ADK installed
- Gemini API key
- SQLite (included with Python)

### Installation

1. **Install dependencies**:
```bash
pip install google-adk sqlite3
```

2. **Set up environment**:
```bash
export GOOGLE_API_KEY=your_gemini_api_key
```

3. **Create sample database**:
```bash
cd app/mcp/adk-mcp-tutorial/local_mcp
python create_db.py
```

4. **Run MCP agent**:
```bash
adk web --agent local_mcp.agent:root_agent
```

## Configuration

### Server Parameters

**Stdio (Local)**:
```python
StdioServerParameters(
    command="python3",  # or "python" on Windows
    args=["/absolute/path/to/server.py"],
    env={"KEY": "value"}  # Optional environment variables
)
```

**HTTP (Remote)**:
```python
HttpServerParameters(
    url="https://mcp-server.example.com",
    headers={"Authorization": "Bearer token"}  # Optional
)
```

### Tool Filtering

**Allow specific tools only**:
```python
MCPToolset(
    connection_params=params,
    tool_filter=['list_tables', 'query']  # Only these tools
)
```

**Allow all tools**:
```python
MCPToolset(
    connection_params=params
    # No tool_filter = all tools available
)
```

## Technical Details

### MCP Protocol

**Key Concepts**:
- **Server**: Provides tools and resources
- **Client**: Consumes tools (ADK agent)
- **Protocol**: Standardized JSON-RPC communication
- **Transport**: Stdio, HTTP, WebSocket

**Message Flow**:
1. Client requests tool list
2. Server responds with available tools
3. Client invokes tool with parameters
4. Server executes and returns result

### Security Considerations

**Tool Filtering**:
- Limit exposed tools for security
- Prevent unauthorized database access
- Reduce attack surface

**Input Validation**:
- Server validates all inputs
- SQL injection prevention
- Type checking

**Process Isolation**:
- Server runs in separate process
- Crashes don't affect agent
- Resource limits can be enforced

### Performance

**Stdio Communication**:
- Low latency for local servers
- Minimal overhead
- Suitable for high-frequency calls

**HTTP Communication**:
- Higher latency
- Better for remote servers
- Supports load balancing

## Integration Points

### With ADK Agents

```python
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

agent = LlmAgent(
    model="gemini-2.0-flash",
    name="db_agent",
    instruction="You can query databases using MCP tools",
    tools=[
        MCPToolset(connection_params=...)
    ]
)
```

### With Unified Application

```python
@app.post("/api/mcp/query")
async def mcp_query(sql: str):
    # Route to MCP agent
    result = await agent.run(f"Execute query: {sql}")
    return result
```

## Observability

### Logging

**Server-side**:
- Tool invocations
- Query execution
- Errors and exceptions
- Performance metrics

**Client-side**:
- Tool discovery
- Tool calls
- Response times
- Connection status

### Metrics to Track
- Tool invocation count
- Average response time
- Error rate
- Database query performance
- Connection failures

## Best Practices

### Server Development
- Validate all inputs rigorously
- Implement proper error handling
- Use connection pooling for databases
- Log all operations for debugging
- Implement rate limiting

### Client Usage
- Use tool filtering for security
- Handle server failures gracefully
- Implement retries for transient errors
- Cache tool lists when possible
- Monitor server health

### Database Operations
- Use parameterized queries (prevent SQL injection)
- Implement read-only mode when appropriate
- Set query timeouts
- Limit result set sizes
- Use transactions for multi-step operations

## Limitations

- **Stdio limitations**: Local servers only
- **No built-in authentication**: Must implement separately
- **Process overhead**: Each server is a separate process
- **Protocol complexity**: More complex than direct function calls
- **Debugging**: Harder to debug cross-process communication

## Future Enhancements

- [ ] Add authentication/authorization
- [ ] Implement connection pooling
- [ ] Add caching layer
- [ ] Support for streaming results
- [ ] WebSocket transport option
- [ ] Tool versioning
- [ ] Health check endpoints
- [ ] Metrics dashboard

## Troubleshooting

### Server Won't Start
```bash
# Check server script path is absolute
# Verify Python executable is correct
# Check file permissions
ls -l /path/to/server.py
```

### Connection Failures
```bash
# Verify server is running
ps aux | grep server.py

# Check logs for errors
# Test server independently
python server.py
```

### Tool Not Found
- Verify tool_filter includes the tool
- Check server implements the tool
- Review server logs for errors

### Database Errors
```bash
# Verify database file exists
ls -l *.db

# Check database permissions
# Test database directly
sqlite3 database.db "SELECT * FROM products;"
```

## References

- [MCP Specification](https://modelcontextprotocol.io/)
- [Google ADK MCP Tools](https://github.com/google/adk)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
