from typing import TypedDict, Annotated
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
import time 
from datetime import datetime,timezone
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.checkpoint.memory import MemorySaver
import ddgs
import httpx
import asyncio

PROMPT_ENDPOINT_URL= "http://127.0.0.1:8000/v1/safeagent/prompt"

memory = MemorySaver()
ddg_search = DuckDuckGoSearchRun()
llm = ChatOllama(model="llama3.2", temperature=0)

class ChatState(TypedDict):
    user: str
    block: bool
    messages: Annotated[list, add_messages]
    tool: list

initial_state = [{'role': 'system','content': 
   """You are a helpful assistant. 

CRITICAL AND MANDATORY RULES:
1. Every user message contains a METADATA section at the top indicating the current time. Use this strictly as your anchor for tracking years, days, or time-sensitive calculations.
2. NEVER include, repeat, mimic, or print the timestamp, date, or time in your response unless the user explicitly asks you what time it is.
3. Maintain a natural, conversational response format. Do not prefix your message with brackets or dates.
4. ONLY use duckduckgo_search to answer questions you are not sure about
5. When you are sure about an answer do not call duckduckgo_search
"""
}]


# @tool
# def check_stock_price(ticker: str):
#     """
#     CRITICAL: ONLY call this tool if the user explicitly mentions a specific stock ticker  or explicitly asks for a financial stock price.
    
#     DO NOT use this tool for greetings, casual conversation, generic questions, 
#     or statements that do not contain a stock symbol. If the user says 'hi', 'hello', 
#     or asks how you are, ignore this tool completely.
#     """
#     print(f'\n\n Checking the price of {ticker} ')
#     prices = {'TSLA': 123.00,'TSMC': 672.0,'SPCX': 108.33,'MTN': 500}
#     if ticker == '':
#         return f'Error you are not supposed to call this tool'
#     return prices[ticker.upper()]

tools  = [ddg_search]
llm_with_tools = llm.bind_tools(tools)
# def prompt_input(state: ChatState) -> ChatState:
#     prompt = input("You:   ")
#     message = {'role':'user','content': f'[Context - Current Time: {datetime.now(timezone.utc)}] \n USER PROMPT: {prompt}'}
#     print(message)
#     initial_state.append(message)
#     state['messages'] = initial_state
#     print(state)
#     return state
def chatbot(state: ChatState):
    assistant = llm_with_tools.invoke(state['messages'])
    message = {'role':'assistant','content': assistant.content}
    # initial_state.append(message)
    print(assistant.tool_calls)
    return {'messages': assistant}
async def prompt_guard_node(state: ChatState):
    print(state["messages"][-1])
    prompt = state["messages"][-1]
    # print(f'/n {prompt}')
    async with httpx.AsyncClient() as client:
        result = await client.post(
            PROMPT_ENDPOINT_URL,
            json={
                "user_id": "test_id",
                "role": "user",
                "prompt": prompt.content  
            }

        )
    output = result.json()
    # print(f'output:  {output['block']}')
    state['block'] = output['block']
    # print(f'\n this is the state after appending block {state}')
    print(f'\nprompt check result:  {output.get('prompt')}')
    prompt.content = output['prompt']
    print(f'\n THIS IS THE INITIAL STATE ⚠️⚠️⚠️:    {state}')
    return state
def prompt_checker(state:ChatState):
    print(f'\nblock status: {state['block']}')
    # return 'block'
    if state["block"] == True:
        return "block"
    else:
        return "allow"
async def tool_guard_node(state: ChatState):
    print(state.get('messages'))
    tool_message =  state.get('messages')[-1]
    async with httpx.AsyncClient(timeout=None) as client:
        result = await client.post(
            "http://127.0.0.1:8000/v1/safeagent/tool_output",
            json={
                "role": "tool",
                "tool_call_id": tool_message.tool_call_id,
                "name": tool_message.name,
                "content": tool_message.content
            }

        )
    print(f'\n this is the tool node result 🛠️: {result.text}')
    tool_message.content = result.text
    print(f'\n this is state after tool output: {state}')
    return state
async def output_guard_node(state: ChatState):
    output = state["messages"][-1]
    async with httpx.AsyncClient(timeout=None) as client:
        result = await client.post(
            "http://127.0.0.1:8000/v1/safeagent/final_output",
            json={
                "output": output.content
            }
        )
    # return result.json()
    output.content = result.text
    print(f'\n this is the final result {result.text}')
    print(f'\n\n\n\n This is the Final State {state}')
    return state
builder = StateGraph(ChatState)

#nodes
# builder.add_node("prompt_input", prompt_input)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))
builder.add_node("prompt_guard_node", prompt_guard_node)
builder.add_node("prompt_status_checker", prompt_checker)
builder.add_node("tool_guard_node", tool_guard_node)
builder.add_node("output_guard_node", output_guard_node)

#edges
builder.add_edge(START,"prompt_guard_node")
builder.add_conditional_edges(

    "prompt_guard_node",
    prompt_checker,
    {
        "block": END,
        "allow": "chatbot"
    }
)
builder.add_conditional_edges('chatbot',tools_condition) #this checks if the llm requests a tool if it does not it ends the graph
# builder.add_edge('chatbot', 'tool_node')
builder.add_edge('tools','tool_guard_node')
builder.add_edge('tool_guard_node', 'chatbot')
builder.add_edge('chatbot', 'output_guard_node')


graph = builder.compile(checkpointer=memory)
async def main():
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC+0")
    config = {"configurable": {"thread_id": "1"}}
    first_turn = True
    while True:
        prompt = input("You:   ")
        message = {'role':'user','content': f"METADATA\nTemporal Anchor: {timestamp}\n\nMessage: {prompt}"}
        # print(message)
        if first_turn:
            initial_state.append(message)
            first_turn = False
            response = await graph.ainvoke({'messages': initial_state}, config=config)
        else:
            response = await graph.ainvoke({'messages': message}, config=config)

asyncio.run(main())