import os
import requests
from flask import Flask, redirect, url_for, request, render_template, jsonify, make_response, Blueprint
import concurrent.futures
import openai
import time
import json

backend = Blueprint('app', __name__)
from octoai.text_gen import ChatMessage

from octoai.client import OctoAI

OCTO_API = os.environ['OCTO_API']
client_openai = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))


client = OctoAI(
    api_key=OCTO_API,
)        
def llm_call(system_message, user_message):
    completion = client.text_gen.create_chat_completion(
        max_tokens=512,
        messages=[
            ChatMessage(
                content=system_message,
                role="system"
            )
        ],
        model="meta-llama-3-8b-instruct",
        presence_penalty=0,
        temperature=0.7,
        top_p=1
    )
    print(completion)
    return completion.choices[0].message.content


def run_assistant(text):
    thread_id = "thread_o2E7ptOKy0MjgvNrCz6CpbA8"
    
    content = [{"type": "text", "text": text}]
    client_openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    run = client_openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id="asst_fidAFGH53AZYfWuiFE3zu3aD"
    )
    while run.status in ["in_progress", "queued"]:
        time.sleep(3)
        run = client_openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if run.status == "completed":
            messages = client_openai.beta.threads.messages.list(thread_id=thread_id)
            message_dict = json.loads(messages.model_dump_json())
            content = message_dict['data'][0]['content'][0]["text"]["value"]
            print("[OPENAI RESPONSE]", content)
            return content
    
    
@backend.route('/retrival', methods=['POST'])
def chat():
    if request.method == 'POST':
        print("[REQUEST RECEIVED]", request.json)
        question = request.json.get('content')
        try :
            # Create a ThreadPoolExecutor with max_workers=2
            # with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            #     # Submit the functions to the executor
            #     future_dem = executor.submit(query_db, question, "dem")
            #     future_rep = executor.submit(query_db, question, "rep")
            #     dem_response = future_dem.result()
            #     rep_response = future_rep.result()
                
            # if dem_response and rep_response:
            #     # TODO return the response
            #     # summarize the response
            #     print("[QUERY OUTPUT]", dem_response, rep_response)
            response = run_assistant(question)

            system_prompt = f"""you are a polical reporter, and you are good at summarize campaign policys.
Given the context from the democratic party and the republican party, summarize the key points of their campaign policies.
Topic : {question}

policies: {response}

return your summary in bullet points. for example:

democrats:
- democrats are focusing on climate change

republicans:
- republicans are focusing on economy 

only include the key points of the policies, no other information needed. 
just go : 
"""
            completion = llm_call(system_prompt, "")
            return jsonify({
                "statusCode": 200,
                "response": completion
            })
            
        except Exception as e:
            return jsonify({
                "statusCode": 500,
                "response": str(e)
            })
        
    return {
            "statusCode": 500
    }


@backend.route('/summarize', methods=['POST'])
def gen_image():
    if request.method == 'POST':
        dem_results = request.json.get('dem_results')
        rep_results = request.json.get('rep_results')
        try:
            pass # TODO here
        except Exception as e:
            return jsonify({
                "statusCode": 500,
                "response": str(e)
            })
    return {
            "statusCode": 500
    }
 