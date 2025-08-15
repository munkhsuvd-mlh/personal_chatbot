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
import datetime

st.set_page_config(
    page_title="Way Academy - Demo chatbot", 
    page_icon="🤖"
)

st.title("Way  Academy - Demo chatbot")
st.info(
    """AI chatbot course deliverable demonstration"""
)

### Environment variables --- Streamlit secrets
# dotenv.load_dotenv()

openai.api_key = st.secrets["OPENAI_API_KEY"]

client = OpenAI()

        
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
assistant_id = 'asst_rTZARYlh6HbrxvIzSqzd91Yk'
    

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
        
    else:
        thread_id = st.session_state.thread_id

    last_prompt = st.session_state.messages[-1]["output"] if st.session_state.messages else prompt
    
    with st.spinner("Хариу бичиж байна..."):
        answer = mlh.thread_response_generator(thread_id, last_prompt, None)

    st.chat_message("assistant").markdown(answer)
    st.session_state.messages.append({"role": "assistant", "output": answer})

    # Re-enable input
    st.session_state.waiting = False
    st.rerun()

        
### Sidebar
# with st.sidebar:
#     st.title("Тестийн чадамж")
#     st.write("1. Тээврийн салбарын бүх нэршил, агуулга")
#     st.write("2. Бүх ажилчдад нээлттэй дотоод журмууд")
#     st.divider()
#     st.write(st.session_state.thread_id)
