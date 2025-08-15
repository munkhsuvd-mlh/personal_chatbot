import pandas as pd
from openai import OpenAI
import ast
import numpy as np
import streamlit as st
import openai
import requests
import dotenv
import os
import re
import json
from dataclasses import dataclass, asdict
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date, datetime

POSTGRES_URL = st.secrets["POSTGRES_URL"]
client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# dotenv.load_dotenv()

# client = OpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY")
# )

# POSTGRES_URL = os.environ.get("POSTGRES_URL")

### Assistant
assistant_id = 'asst_d3D7Oze5S6AZIz5GuT6rDnUT'

def web_search_result(question: str):
    response = client.responses.create(
        model="gpt-4.1",
        tools=[{"type": "web_search_preview"}],
        input=question
    )
    return response.output_text


    
# today = datetime.now().strftime('%Y-%m-%d')

def thread_response_generator(thread_id: str, new_message: str, user_id: str | None):
    ### Adding a new message from user to the thread using thread_id
    
    message = client.beta.threads.messages.create(
      thread_id=thread_id,
      role="user",
      content=new_message
    )
    run = client.beta.threads.runs.create_and_poll(
      thread_id=thread_id,
      assistant_id=assistant_id,
    )
    run_id = run.id
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
        thread_id=thread_id
        )
        answer = messages.data[0].content[0].text.value
        answer = re.sub(r'\d+:\d+†', '', answer)
        return answer
        
    elif run.status == 'requires_action':
        tool_outputs = []
 
        # Loop through each tool in the required action section
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == 'get_current_info':
                args_str = tool.function.arguments 
                args = json.loads(args_str)

                question = args['question']
                output = web_search_result(question)
                # output_str = json.dumps(output)


                tool_outputs.append({
                  "tool_call_id": tool.id,
                  "output": output
                })
                
        if tool_outputs:
            try:
                run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread_id,
                    run_id=run_id,
                    tool_outputs=tool_outputs
                )
                if run.status == 'completed':
                    messages = client.beta.threads.messages.list(
                        thread_id=thread_id
                      )
                    answer = messages.data[0].content[0].text.value
                    return answer
                    
            except Exception as e:
                return f"Failed to submit tool outputs: {e}"
        else:
            return "No tool outputs to submit."
         
    else:
        return 'a'


