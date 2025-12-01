import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
# Use your working key from the .env file or hardcode if testing
os.environ["OPENWEATHERMAP_API_KEY"] = "9e20f5fe1109135f48d6b5e854015184"

# Initialize the LLM using Groq
def initialize_llm():
    """Initialize the LLM using ChatGroq."""
    if not groq_api_key:
        st.error("GROQ_API_KEY not found. Please check your .env file.")
        st.stop()
        
    return ChatGroq(
        model="qwen/qwen3-32b", # Llama3 is highly optimized for tool use
        groq_api_key=groq_api_key,
        temperature=0
    )

# 1. Guardrail Logic (Kept as requested)
def check_guardrails(query, llm):
    """Checks if the query is relevant to weather."""
    system_instruction = """
    You are a strict guardrail agent. 
    Your ONLY job is to classify if the user's input is asking about the weather, temperature, humidity, or forecast.
    
    - If the input IS about weather, reply with exactly one word: YES
    - If the input is NOT about weather (e.g., general knowledge, math, coding, history, greetings), reply with exactly one word: NO
    """
    
    prompt = ChatPromptTemplate.from_template(
        """
        {system_instruction}
        User Input: {query}
        """
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"system_instruction": system_instruction, "query": query})
    
    if "YES" in response.strip().upper():
        return True
    return False

# 2. Agent Setup (THE FIX)
def create_weather_agent(llm):
    """Creates an agent that can use the Weather Tool."""
    
    # Define the tool
    weather_wrapper = OpenWeatherMapAPIWrapper()
    weather_tool = Tool(
        name="Weather",
        func=weather_wrapper.run,
        description="Useful for fetching current weather information. Input should be a city name (e.g. London,GB)."
    )
    tools = [weather_tool]

    # Define the Agent's Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful weather assistant. Use the Weather tool to fetch real-time data."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Construct the Tool Calling Agent
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Create the Executor (This runs the agent)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor

# Streamlit UI
def main():
    st.set_page_config(page_title="Weather Bot", layout="wide")
    st.title("⚡ Interactive Weather Chatbot")
    
    query_input = st.text_input("Ask a question (e.g., 'What is the weather in London?'):")
    
    llm = initialize_llm()

    if query_input:
        with st.spinner("Processing Guardrails..."):
            is_allowed = check_guardrails(query_input, llm)
            
        if is_allowed:
            with st.spinner("Agent is thinking..."):
                # Initialize the agent
                agent_executor = create_weather_agent(llm)
                
                # Run the agent (It automatically handles city extraction + tool calling)
                try:
                    response = agent_executor.invoke({"input": query_input})
                    
                    st.success("Guardrail Passed ✅")
                    st.write("### Response:")
                    st.write(response['output'])
                    
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.error("Guardrail Blocked 🛑")
            st.write("I do not have the information.")

if __name__ == "__main__":
    main()