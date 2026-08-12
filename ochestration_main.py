from typing import TypedDict, Annotated
from langchain_core.tools import tool
from langgraph.graph import StateGraph,START,END
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from send_email import send_email_to_user
from datetime import datetime, timezone
from langgraph.prebuilt import ToolNode, tools_condition
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
import time
from langchain.chat_models import init_chat_model
from auth.core.settings import settings
class EmailState(TypedDict):
    email: str
    messages: Annotated[list, add_messages]


#memory
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)

current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC+0")


initial_message = [{"role": "system","content": 
                    f"""

                    CRITICAL AND MANDATORY RULES:
                    1. This is the current time {current_time}. YOU ALREADY KNOW THIS. Answer time-related questions directly using this provided timestamp.
                    2. Do NOT attempt to call a tool to find the date or time use {current_time} to answer any time related questions
                    3. NEVER include, repeat, mimic, or print the timestamp, date, or time in your response unless the user EXPLICITLY ASKS you what time or date related questions it is.
                    4. IF the user sends a greeting or casual message (e.g., "hello", "what's up"), you MUST act as a conversational chatbot and respond with a friendly text greeting. 
                    5. IF AND ONLY IF the user explicitly asks you to send an email, you may use the send_email_to_user tool.
                    """
                    }]

#tool definitions
send_email = tool(send_email_to_user)
tools = [send_email]

#llm initialization
llm = init_chat_model("google_genai:gemini-3.1-flash-lite",api_key = settings.GEMINI_API_KEY)
# llm = ChatOllama(model="llama3.2", temperature=0)
# llm = ChatOllama(model="qwen2.5:3b", temperature=0)
llm_with_tools = llm.bind_tools(tools)

#chatbot node functions creation
def chatbot(state: EmailState):
    """this is the chatbot node"""
    print("activating chatbot")
    t = time.time()
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": response}
builder = StateGraph(EmailState)

#nodes 
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))

#edges 
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", END)

graph = builder.compile(checkpointer=memory)


def call_graph(prompt,config):
    state = graph.get_state(config)
    if state.values:
        dummy = graph.invoke({'messages': [prompt]}, config=config)

    else:
        initial_message.append(prompt)
        dummy = graph.invoke({'messages': initial_message}, config=config)
    try:
        if dummy.get("__interrupt__") != None:
            return dummy["__interrupt__"][0].value
        else:
            return {"body": "this does not require email tool"}
    except:
        return {"status": "this does not require email call"}
