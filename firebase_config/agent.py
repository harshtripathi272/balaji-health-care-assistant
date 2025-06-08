from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from firebase_config.tools import all_tools
import os
from firebase_config.llama_index_configs import global_settings  # triggers embedding config

# Load Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=GOOGLE_API_KEY
)

# Initialize conversational memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Create LangChain agent with tools and memory
agent = initialize_agent(
    tools=all_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

# Wrapper function to call the agent
def run_agent(user_input: str) -> str:
    return agent.run(user_input)
