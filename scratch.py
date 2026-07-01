from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool

@tool
def add(a:int, b:int) -> int:
    """Add two numbers"""
    return a+b

llm = ChatGoogleGenerativeAI(model='gemini-1.5-flash')
agent = create_react_agent(llm, tools=[add])
print('OK')
