import os
import streamlit as st
from langchain_groq.chat_models import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def initialize_llm():
    """Initialize the LLM using the Groq"""
    model = ChatGroq(model="gemma2-9b-it", groq_api_key=groq_api_key)
    return model

def behaviour_llm(model, choice, language, text):
    """LLM behaviour"""
    parser = StrOutputParser()  # Initialize parser here for use in different choices
    
    if choice == 1:
        messages = [
            SystemMessage(content=f"Translate the following from Hindi to {language}"),
            HumanMessage(content=text)
        ]
        result = model.invoke(messages)

    elif choice == 2:
        messages = [
            SystemMessage(content=f"Translate the following from Hindi to {language}"),
            HumanMessage(content=text)
        ]
        result = model.invoke(messages)
        result = parser.invoke(result)

    elif choice == 3:
        messages = [
            SystemMessage(content=f"Translate the following from English to {language}"),
            HumanMessage(content=text)
        ]
        chain = model | parser
        result = chain.invoke(messages)

    elif choice == 4:
        generic_template = "Translate the following into {language}:"
        prompt = ChatPromptTemplate.from_messages(
            [("system", generic_template), ("user", "{text}")]
        )
        chain = prompt | model | parser
        result = chain.invoke({"language": language, "text": text})

    else:
        return "Invalid choice"
    
    return result

# Streamlit UI setup
def main():
    st.title("Language Translator using LCEL techniques")
    st.markdown("Use this app to Translate any text article into your desired language")

    # Input fields for translation
    language_input = st.text_input("Enter the language you want to convert your text into:")
    text_input = st.text_input("Enter the text to be converted:")
    choice_input = st.number_input("Enter the choice number", min_value=1, max_value=4, value=1)

    # Sidebar for additional info
    st.sidebar.markdown("### How to Use:")
    st.sidebar.markdown("""
    Step 1. Enter a language in which you want to convert your text. \n
    Step 2. Enter the text to be converted. \n
    Step 3. Get an AI-generated answer based on the choice of Langchain expression to be used. The choices are:\n
    1. Result from system message and human message.\n
    2. Result from system message and human message with output parser.\n
    3. Result from system message and human message with output parser and model. \n
    4. Result from system message and human message with output parser and model with generic template.\n
    """)

    # Initialize the LLM
    llm = initialize_llm()

    # If input is provided, perform translation
    if language_input and text_input:
        with st.spinner("Loading and processing the text..."):
            result = behaviour_llm(llm, choice_input, language_input, text_input)
        
        # Display response
        with st.spinner("Generating answer..."):
            st.write("### Response:")
            st.write(result)

if __name__ == "__main__":
    main()
