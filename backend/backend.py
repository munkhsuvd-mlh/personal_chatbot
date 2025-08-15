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

openai.api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI()



# dotenv.load_dotenv()

# client = OpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY")
# )

# POSTGRES_URL = os.environ.get("POSTGRES_URL")

### Assistant
assistant_id = 'asst_rTZARYlh6HbrxvIzSqzd91Yk'

    
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
