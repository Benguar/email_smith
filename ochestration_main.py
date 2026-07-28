from typing import TypedDict, Annotated
from langchain_core.tools import tool
from langgraph.graph import StateGraph,START,END
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from send_email import send_email_to_user
from datetime import datetime, timezone
from langgraph.prebuilt import ToolNode, tools_condition

#initial state

class EmailState(TypedDict):
    email: str
    messages: Annotated[list, add_messages]




current_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H UTC+0")


initial_message = [{"role": "system","content": 
                    f"""

                    CRITICAL AND MANDATORY RULES:
                    1. This is the current time {current_time}. Use this strictly as your anchor for tracking years, days, or time-sensitive calculations.
                    2. NEVER include, repeat, mimic, or print the timestamp, date, or time in your response unless the user explicitly asks you what time it is.
                    3. Maintain a natural, conversational response format. Do not prefix your message with brackets or dates.
                    4. ONLY use send_email_tool when do user asks you to send a mail
                    5. NEVER use it for casual conversations, greetings or anything not related toi sending a  mail
                    """
                    }]


#tool definitions
send_email = tool(send_email_to_user)
tools = [send_email]

#ollama initiialization
llm = ChatOllama(model="llama3.2", temperature=0)
llm_with_tools = llm.bind_tools(tools)

#chatbot node functions creation
def chatbot(state: EmailState):
    """this is the chatbot node"""
    response = llm_with_tools.invoke(state["messages"])
    print(f' \n {response}')
    return {"messages": response}
# print(llm.invoke("hey"))
builder = StateGraph(EmailState)

#nodes 
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))

#edges 
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", END)

graph = builder.compile()

test = input("User:   ")
message = initial_message.append({"role": "user", "content": test})
graph.invoke({'messages': initial_message})