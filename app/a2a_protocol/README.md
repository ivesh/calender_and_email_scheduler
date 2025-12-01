# A2A Protocol - Agent-to-Agent Communication

## Overview

The A2A (Agent-to-Agent) Protocol implementation demonstrates how autonomous agents can communicate and collaborate to accomplish complex tasks. This showcases distributed agent architectures where multiple agents work together, each with their own capabilities and knowledge.

## Key Features

### 🤝 Agent Collaboration
- **Peer-to-peer communication**: Agents communicate directly
- **Protocol-based interaction**: Standardized message formats
- **Autonomous decision-making**: Each agent operates independently
- **Distributed problem-solving**: Complex tasks split across agents
- **Asynchronous communication**: Non-blocking agent interactions

### 🚀 Available Implementations

#### 1. Simple A2A Agent
Basic agent-to-agent communication example.

#### 2. Friend Scheduling Multi-Agent System
Advanced multi-agent orchestration for meeting scheduling.

## Architecture

### Simple A2A Agent (`a2a_simple/`)

#### Purpose
Demonstrates fundamental A2A protocol concepts with minimal complexity.

#### Components
- **Single Agent**: Basic A2A-enabled agent
- **Test Client**: Invokes the agent via A2A protocol
- **Protocol Handler**: Manages A2A message exchange

#### Use Case
- Learning A2A basics
- Testing protocol implementation
- Building blocks for complex systems

#### Message Flow
```
Client → A2A Request → Agent → Process → A2A Response → Client
```

### Friend Scheduling System (`a2a_friend_scheduling/`)

#### Purpose
Multi-agent system where a host agent coordinates with multiple friend agents to schedule a meeting.

#### Agents

**Host Agent**
- **Role**: Meeting organizer
- **Responsibilities**:
  - Initiate scheduling request
  - Communicate with friend agents
  - Collect availability
  - Determine optimal meeting time
  - Confirm with all participants

**Friend Agents** (Multiple)
- **Role**: Meeting participants
- **Responsibilities**:
  - Receive scheduling requests
  - Check personal calendar
  - Respond with availability
  - Confirm or decline meeting

**Kaitlynn Agent** (LangGraph Implementation)
- **Special**: Implemented using LangGraph
- **Features**: State management, complex workflows
- **Integration**: Works seamlessly with other A2A agents

#### Workflow
```
Host Agent: "Let's schedule a meeting for next week"
    ↓
Host → Friend 1: "Are you available Tuesday 2-3 PM?"
Host → Friend 2: "Are you available Tuesday 2-3 PM?"
Host → Friend 3: "Are you available Tuesday 2-3 PM?"
    ↓
Friend 1 → Host: "Yes, I'm available"
Friend 2 → Host: "No, I have a conflict"
Friend 3 → Host: "Yes, I'm available"
    ↓
Host: Analyzes responses, finds alternative time
    ↓
Host → Friend 2: "How about Wednesday 3-4 PM?"
    ↓
Friend 2 → Host: "Yes, that works"
    ↓
Host: "Meeting scheduled for Wednesday 3-4 PM"
    ↓
Host → All Friends: "Confirmed: Wednesday 3-4 PM"
```

## Protocol Specifications

### A2A Message Format

```python
{
    "protocol": "a2a/1.0",
    "message_type": "request" | "response" | "notification",
    "from": "agent_id",
    "to": "agent_id",
    "conversation_id": "unique_id",
    "timestamp": "ISO8601",
    "payload": {
        # Message-specific data
    }
}
```

### Message Types

#### Request
```python
{
    "message_type": "request",
    "payload": {
        "action": "check_availability",
        "parameters": {
            "date": "2024-06-15",
            "time_range": "14:00-15:00"
        }
    }
}
```

#### Response
```python
{
    "message_type": "response",
    "payload": {
        "status": "success" | "error",
        "result": {
            "available": true,
            "conflicts": []
        }
    }
}
```

#### Notification
```python
{
    "message_type": "notification",
    "payload": {
        "event": "meeting_confirmed",
        "details": {
            "time": "2024-06-15T14:00:00Z",
            "participants": ["agent1", "agent2"]
        }
    }
}
```

## Usage Examples

### Simple A2A Agent

**Start Agent**:
```bash
cd app/a2a_protocol/agent2agent/a2a_simple
python agent.py
```

**Test Client**:
```bash
python client.py
```

**Example Interaction**:
```python
# Client sends request
client.send_request({
    "action": "greet",
    "name": "Alice"
})

# Agent responds
{
    "status": "success",
    "message": "Hello, Alice!"
}
```

### Friend Scheduling System

**Start Host Agent**:
```bash
cd app/a2a_protocol/agent2agent/a2a_friend_scheduling
python host_agent.py
```

**Start Friend Agents**:
```bash
# Terminal 1
python friend_agent.py --name Alice --port 5001

# Terminal 2
python friend_agent.py --name Bob --port 5002

# Terminal 3 (LangGraph agent)
python kaitlynn_agent_langgraph/agent.py --port 5003
```

**Initiate Scheduling**:
```bash
python schedule_meeting.py --topic "Project Review" --duration 60
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- A2A Python SDK
- Google ADK (for ADK-based agents)
- LangGraph (for Kaitlynn agent)

### Installation

1. **Install dependencies**:
```bash
pip install a2a-sdk google-adk langgraph
```

2. **Clone A2A samples** (optional):
```bash
git clone https://github.com/google-a2a/a2a-samples
```

3. **Run simple example**:
```bash
cd app/a2a_protocol/agent2agent/a2a_simple
python agent.py
```

4. **Run friend scheduling**:
```bash
cd app/a2a_protocol/agent2agent/a2a_friend_scheduling
# Follow README.md in that directory
```

## Configuration

### Agent Configuration

```python
from a2a import Agent, AgentConfig

config = AgentConfig(
    agent_id="friend_alice",
    name="Alice",
    capabilities=["calendar", "scheduling"],
    endpoint="http://localhost:5001"
)

agent = Agent(config)
```

### Communication Settings

```python
# Timeout for agent responses
timeout = 30  # seconds

# Retry policy
max_retries = 3
retry_delay = 1  # seconds

# Message queue size
queue_size = 100
```

## Technical Details

### A2A SDK

**Core Components**:
- **Agent**: Base class for A2A-enabled agents
- **Protocol Handler**: Manages message serialization/deserialization
- **Transport**: HTTP, WebSocket, or custom
- **Discovery**: Agent discovery and registration

**Agent Lifecycle**:
1. Initialize agent with config
2. Register capabilities
3. Start listening for messages
4. Process incoming requests
5. Send responses
6. Handle errors and timeouts

### LangGraph Integration (Kaitlynn Agent)

**State Management**:
```python
from langgraph.graph import StateGraph

class SchedulingState(TypedDict):
    requests: List[Request]
    availability: Dict[str, bool]
    confirmed_time: Optional[str]

graph = StateGraph(SchedulingState)
```

**Benefits**:
- Complex decision logic
- State persistence
- Conditional workflows
- Error recovery

### Communication Patterns

#### Request-Response
```
Agent A → Request → Agent B
Agent A ← Response ← Agent B
```

#### Publish-Subscribe
```
Agent A → Notification → All Subscribers
```

#### Orchestration
```
Orchestrator → Request → Agent 1
Orchestrator → Request → Agent 2
Orchestrator ← Response ← Agent 1
Orchestrator ← Response ← Agent 2
Orchestrator → Decision → All Agents
```

## Integration Points

### With ADK Agents

```python
from google.adk.agents import Agent
from a2a import A2ACapability

adk_agent = Agent(
    name="jarvis",
    model="gemini-2.0-flash",
    capabilities=[A2ACapability()]  # Enable A2A
)
```

### With Unified Application

```python
@app.post("/api/a2a/schedule-meeting")
async def schedule_meeting(request: MeetingRequest):
    # Invoke host agent
    host = HostAgent()
    result = await host.schedule_meeting(
        participants=request.participants,
        duration=request.duration
    )
    return result
```

## Observability

### Logging

**Agent-level**:
- Incoming/outgoing messages
- Processing time
- Errors and exceptions
- State changes

**System-level**:
- Agent discovery events
- Connection status
- Message routing
- Performance metrics

### Metrics to Track
- Message latency (end-to-end)
- Agent response time
- Success/failure rates
- Active conversations
- Agent availability
- Network errors

## Best Practices

### Agent Design
- **Single responsibility**: Each agent has clear purpose
- **Stateless when possible**: Easier to scale and debug
- **Idempotent operations**: Handle duplicate messages
- **Graceful degradation**: Work with partial information

### Communication
- **Use timeouts**: Don't wait forever for responses
- **Implement retries**: Handle transient failures
- **Validate messages**: Check format and content
- **Log everything**: Essential for debugging distributed systems

### Error Handling
- **Timeout handling**: What to do when agent doesn't respond
- **Partial failures**: Some agents succeed, others fail
- **Conflict resolution**: Agents disagree on outcome
- **Recovery strategies**: How to resume after errors

## Limitations

- **Network dependency**: Requires reliable network
- **Complexity**: Distributed systems are harder to debug
- **Latency**: Multi-agent coordination takes time
- **Consistency**: Ensuring all agents have same view
- **Discovery**: Finding and connecting to agents

## Future Enhancements

- [ ] Add agent discovery service
- [ ] Implement message persistence
- [ ] Add authentication/authorization
- [ ] Create monitoring dashboard
- [ ] Support for agent groups
- [ ] Implement consensus protocols
- [ ] Add circuit breakers
- [ ] Create agent marketplace

## Troubleshooting

### Agent Not Responding
```bash
# Check agent is running
curl http://localhost:5001/health

# Check network connectivity
ping localhost

# Review agent logs
tail -f agent.log
```

### Message Delivery Failures
- Verify agent endpoints are correct
- Check firewall rules
- Review message format
- Check timeout settings

### Scheduling Conflicts
- Verify calendar integration
- Check time zone handling
- Review conflict resolution logic
- Test with simpler scenarios

### LangGraph Agent Issues
```bash
# Verify LangGraph installation
pip show langgraph

# Check state persistence
# Review graph definition
# Test state transitions independently
```

## References

- [A2A Protocol Specification](https://github.com/google/a2a-python)
- [A2A Python SDK](https://github.com/google/a2a-python)
- [A2A Samples](https://github.com/google-a2a/a2a-samples)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Distributed Systems Patterns](https://martinfowler.com/articles/patterns-of-distributed-systems/)
