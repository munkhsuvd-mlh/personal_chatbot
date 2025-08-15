import streamlit as st
import time
import pandas as pd
import numpy as np
import os
import requests
import openai
import json
import re
from openai import OpenAI
import backend.backend as mlh 
import dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime

st.set_page_config(
    page_title="MonLogistics Group Chatbot", 
    page_icon="🤖"
)

st.title("MLG ажилтны туслах")
st.info(
    """Тестийн хувилбар"""
)

### Environment variables --- Streamlit secrets
# dotenv.load_dotenv()

openai.api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI()

POSTGRES_URL = st.secrets["POSTGRES_URL"]


def get_user_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        ip = response.json()["ip"]
        return ip
    except:
        return "Unable to get IP"
        
### Chat Session Control

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "output" in message.keys():
            st.markdown(message["output"])
            
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
    
if "waiting" not in st.session_state:
    st.session_state.waiting = False


### Assistant
assistant_id = 'asst_d3D7Oze5S6AZIz5GuT6rDnUT'
    

### Chat user prompt & response generation

prompt = st.chat_input("Танд юугаар туслах вэ?", disabled=st.session_state.waiting)

if prompt:
    # Disable input while waiting for response
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "output": prompt})
    
    st.session_state.waiting = True
    st.rerun()

today = datetime.datetime.now().strftime('%Y-%m-%d')

if st.session_state.waiting:
    if st.session_state.thread_id is None:
        thread = client.beta.threads.create()
        thread_id = thread.id
        st.session_state.thread_id = thread_id

        message = client.beta.threads.messages.create(
          thread_id=thread_id,
          role="assistant",
          content="Today's date is" + today,
        )

        conn = psycopg2.connect(POSTGRES_URL)
        cur = conn.cursor()
    
        insert_query = """
            INSERT INTO mlh_chat_threads (
                thread_id, channel, ip, assistant_type, created_at
            ) VALUES (%s, %s, %s, %s, %s);
        """
    
        cur.execute(insert_query, (
            thread_id,
            "web",
            get_user_ip(),
            "employee",
            datetime.datetime.now()
        ))
    
        conn.commit()
        
    else:
        thread_id = st.session_state.thread_id

    # Get last user prompt (saved before rerun)
    #last_prompt = st.session_state.messages[-1]["output"] if st.session_state.messages else prompt

    # Add user message if it's not already added
    # if not st.session_state.messages or st.session_state.messages[-1]["role"] != "user":
    # st.chat_message("user").markdown(prompt)
    # st.session_state.messages.append({"role": "user", "output": prompt})

    last_prompt = st.session_state.messages[-1]["output"] if st.session_state.messages else prompt
    
    with st.spinner("Хариу бичиж байна..."):
        answer = mlh.thread_response_generator(thread_id, last_prompt, None)

    st.chat_message("assistant").markdown(answer)
    st.session_state.messages.append({"role": "assistant", "output": answer})

    # Re-enable input
    st.session_state.waiting = False
    st.rerun()

        
### Sidebar
with st.sidebar:
    st.title("Тестийн чадамж")
    st.write("1. Тээврийн салбарын бүх нэршил, агуулга")
    st.write("2. Бүх ажилчдад нээлттэй дотоод журмууд")
    st.divider()
    st.write(st.session_state.thread_id)
