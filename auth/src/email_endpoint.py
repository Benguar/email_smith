import sys
import os
sys.path.append(os.getcwd())
from fastapi import APIRouter, Request,Response
from auth.schemas.classes import SendPrompt,ResumePrompt
from langgraph.types import Command
from ochestration_main import call_graph,graph
import asyncio
from uuid6 import uuid7
route = APIRouter()

refresh_token = None


@route.post("/send_prompt")
def send_email(prompt: SendPrompt,request: Request, response: Response):
    # global hey
    print("hey")
    global refresh_token
    refresh_token = request.cookies.get("refresh_token")
    thread_id = request.cookies.get("thread_id")
    print(thread_id)
    config = {"configurable": {"thread_id": thread_id,"refresh_token": refresh_token,"email":prompt.email}}
    prompt_dictionary = {"role": "user", "content": prompt.prompt}
    print(prompt_dictionary)
    hey =  call_graph(prompt_dictionary,config)
    print(f'this is what hey returns {hey}')  
    return hey
@route.post("/resume")
def resume_graph(resume: ResumePrompt, request: Request,response: Response):
    print(resume)
    decision= {
        "decision": resume.decision,
        "recipient_email": resume.recipient_email,
        "subject": resume.subject,
        "body": resume.body

    }
    refresh_token = request.cookies.get("refresh_token")
    thread_id = request.cookies.get("thread_id")
    print(thread_id)
    config = {"configurable": {"thread_id": thread_id,"refresh_token": refresh_token,"email": resume.email}}
    boy = graph.invoke(Command(resume=decision), config=config)
    print(boy["messages"][-1])
    response.set_cookie(
         key="thread_id",
        value=str(uuid7()),
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
    )
    return boy["messages"][-1].content


