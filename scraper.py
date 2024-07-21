import os
import json
import re
import requests

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

import chromadb
from chromadb.config import Settings
import uuid


# client = chromadb.HttpClient(host='54.177.175.103', port=8000)

load_dotenv()

# set api keys
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
os.environ['SERPER_API_KEY'] = os.getenv('SERPER_API_KEY')

OPENAI_BASE_URL="https://text.octoai.run/v1"
OCTOAI_API_KEY= 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjNkMjMzOTQ5In0.eyJzdWIiOiI3NzIxOGRmOS03YjVmLTQ2YWUtYTM0MS02ZjM0MzQxMGZkMTgiLCJ0eXBlIjoidXNlckFjY2Vzc1Rva2VuIiwidGVuYW50SWQiOiI3MDJjOThiMy02YTVhLTRhYTQtOGE2MC1kNzdjNzU4NmYwYjciLCJ1c2VySWQiOiJjODk0ZGFjZC01NWIwLTQ5YTAtODdhYy0zNzQ0MzI4MDBiMjAiLCJhcHBsaWNhdGlvbklkIjoiYTkyNmZlYmQtMjFlYS00ODdiLTg1ZjUtMzQ5NDA5N2VjODMzIiwicm9sZXMiOlsiRkVUQ0gtUk9MRVMtQlktQVBJIl0sInBlcm1pc3Npb25zIjpbIkZFVENILVBFUk1JU1NJT05TLUJZLUFQSSJdLCJhdWQiOiIzZDIzMzk0OS1hMmZiLTRhYjAtYjdlYy00NmY2MjU1YzUxMGUiLCJpc3MiOiJodHRwczovL2lkZW50aXR5Lm9jdG8uYWkiLCJpYXQiOjE3MjE1MTExMTF9.oe1yLhkNXH1cBnIo2o2dOll03XhOtOuO7K94lKOdQWs-Ve1OZDuPi4Ptu1zDoQ7i5NloHDIR5Zcu01BeT_jLT9F3nSBz7tBNLq8CsNoWIpCeRYbPcZTi2DquL1bC9JohEaQH00yJYyKpqzYcd-gjFhRiOvwUuabTYe0-2d2yLNANEAFYh-aaY9JqFNVKhi1SPVNtC7_mafcle1HWRxT4cpNgsRcVVsioL5Gpb6ndM5j37zel1t4bT4-n1MfCO3w3HtuT7ZXUGmcXV-Gc2czrTwzJj8_NiTF-nIU7Ys8zU9F9Iuk8hN0GJpt5I6zRw64icmp-c-hjEUiw9ioPnspbSw'

from chromadb.config import Settings

# Define the custom embedding function class
class CustomEmbeddingFunction:
    def __init__(self, model_name):
        self.model_name = model_name

    def __call__(self, input):
        url = "https://text.octoai.run/v1/embeddings"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OCTOAI_API_KEY}"
        }
        data = {
            "input": input,
            "model": self.model_name
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to get embedding: {response.text}")
        return response.json()["data"]

# Initialize the custom embedding function
# embedding_function = CustomEmbeddingFunction("thenlper/gte-large")

# Initialize the tool for internet searching capabilities
search_tool = SerperDevTool(api_key=os.getenv('SERPER_API_KEY'))

#querys to scrape from google
queries = [
    "Joe Biden 2024 economic policies",
    "Biden vs Trump policy comparison 2024 election",
    "Joe Biden campaign promises for second term",
    "Donald Trump 2024 campaign policy agenda",
    "Biden administration accomplishments and future plans",
    "Trump 2024 economic policy proposals",
    "Biden climate change policy 2024 campaign",
    "Trump immigration reform plans 2024",
    "Biden healthcare policy for 2024 election",
    "Trump foreign policy goals 2024 campaign",
    "Biden education reform proposals 2024",
    "Trump energy policy 2024 election platform",
    "Biden tax plan for second term",
    "Trump infrastructure investment proposals 2024",
    "Biden 2024 campaign stance on gun control",
    "Trump cybersecurity policy for 2024 presidency",
    "Biden plan for student loan debt 2024 election",
    "Trump 2024 campaign social security reform proposals",
    "Biden foreign policy priorities for second term",
    "Trump 2024 campaign criminal justice reform plans",
    "Biden renewable energy initiatives for 2024",
    "Trump trade policy and tariffs 2024 campaign",
    "Biden mental health policy proposals 2024",
    "Trump 2024 campaign technology and AI strategy",
    "Biden minimum wage increase plans 2024",
    "Trump policies on veterans’ benefits 2024",
    "Biden plans for affordable housing 2024",
    "Trump judicial appointments 2024 campaign",
    "Biden strategies for reducing income inequality 2024",
    "Trump stance on public transportation improvements 2024",
    "Biden infrastructure modernization plans 2024",
    "Trump approach to drug policy and regulation 2024",
    "Biden efforts to combat homelessness 2024",
    "Trump foreign trade agreements 2024 election",
    "Biden strategies for combating racial inequality 2024",
    "Trump policies on renewable energy investment 2024",
    "Biden approaches to cybersecurity 2024 campaign",
    "Trump strategies for reducing national debt 2024",
    "Biden support for small businesses 2024 election",
    "Trump positions on military spending 2024",
    "Biden policies on worker rights and protections 2024",
    "Trump campaign plans for defense and security 2024",
    "Biden responses to healthcare accessibility issues 2024",
    "Trump plans for reforming the tax code 2024",
    "Biden strategies for educational equity 2024",
    "Trump views on international climate agreements 2024",
    "Biden plans for enhancing public health 2024",
    "Trump policies on international diplomacy 2024",
    "Biden proposals for internet privacy and security 2024",
    "Trump strategies for managing federal budget 2024",
    "Biden initiatives for urban development 2024",
    "Trump policies on gun rights and regulation 2024",
    "Biden stance on family and medical leave policies 2024",
    "Trump plans for military veterans 2024",
    "Biden proposals for federal student aid 2024",
    "Trump views on immigration and border control 2024",
    "Biden climate action plans for 2024",
    "Trump economic recovery strategies 2024",
    "Biden plans for clean energy jobs 2024",
    "Trump policies on trade deficits and surpluses 2024",
    "Biden positions on labor union support 2024",
    "Trump views on criminal justice system reform 2024",
    "Biden strategies for rural development 2024",
    "Trump policies on industrial regulation 2024",
    "Biden proposals for environmental protection 2024",
    "Trump policies on health insurance reform 2024",
    "Biden campaign plans for global leadership 2024",
    "Trump economic stimulus proposals 2024",
    "Biden plans for combating climate change 2024",
    "Trump policies on economic growth and job creation 2024",
    "Biden healthcare coverage expansion plans 2024",
    "Trump views on federal and state relations 2024",
    "Biden strategies for improving access to education 2024",
    "Trump positions on government spending and debt 2024",
    "Biden proposals for reducing carbon emissions 2024",
    "Trump policies on tax cuts and business incentives 2024",
    "Biden approaches to managing national security threats 2024",
    "Trump positions on foreign aid and diplomacy 2024",
    "Biden policies on infrastructure development 2024",
    "Trump views on federal regulations and oversight 2024",
    "Biden strategies for healthcare system improvements 2024",
    "Trump policies on border security and immigration reform 2024",
    "Biden plans for modernizing public schools 2024",
    "Trump economic policies on job creation and wages 2024",
    "Biden approaches to mental health support 2024",
    "Trump policies on economic inequality 2024",
    "Biden plans for reducing gun violence 2024",
    "Trump views on international trade policies 2024",
    "Biden strategies for public safety and crime reduction 2024",
    "Trump policies on environmental conservation 2024",
    "Biden plans for improving veterans’ services 2024",
    "Trump positions on tax reform and economic incentives 2024",
    "Biden policies on affordable healthcare 2024",
    "Trump views on global environmental issues 2024",
    "Biden strategies for supporting the working class 2024",
    "Trump plans for enhancing national defense 2024",
    "Biden proposals for renewable energy research 2024",
    "Trump policies on federal education funding 2024",
    "Biden approaches to income tax reform 2024",
    "Trump positions on economic policies for innovation 2024",
    "Biden plans for addressing income disparities 2024",
    "Trump strategies for promoting American industry 2024",
    "Biden policies on public health and safety 2024",
    "Trump views on international trade negotiations 2024",
    "Biden plans for supporting arts and culture 2024",
    "Trump policies on environmental impact regulations 2024",
    "Biden strategies for enhancing cybersecurity infrastructure 2024",
    "Trump economic policies on manufacturing jobs 2024",
    "Biden approaches to reducing greenhouse gas emissions 2024",
    "Trump views on national economic strategy 2024",
    "Biden proposals for improving social services 2024",
    "Trump policies on international partnerships and alliances 2024",
    "Biden plans for supporting technology and innovation 2024",
    "Trump approaches to reducing federal deficits 2024"
]

# agent to summarize info
writer_agent = Agent(
    role='Political newsletter writer',
    goal='deliver unbiased summary of political data',
    backstory="""You are a renowned author in a political newsletter, known for your unbiased papers.
    You clearly answer questions about politics and the 2024 election between Trump and Biden.""",
    verbose=True,
    allow_delegation=False,
    llm=ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.3),
)

def get_serper_api_results(prompt):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": prompt})
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

def get_top_3_links_with_metadata(response_data):
    organic_results = response_data.get('organic', [])
    top_3_links = []
    for result in organic_results[:3]:
        link_data = {
            "url": result.get('link', '')
        }
        top_3_links.append(link_data)
    return top_3_links


def get_summary(query):
    task = Task(
        description=f"Write in an unbiased and proffesional matter, focusing on facts. Summarize the following information about '{query}'",
        expected_output="Conduct comprehensive analysis and summarize in a few bullet points",
        agent=writer_agent
    )
    return task.execute()

def extract_info_from_query(query):
    candidate = "Joe Biden" if "Biden" in query else "Donald Trump"
    # policy_area = re.search(r'(\w+) policies', query).group(1).lower() #regex to define the policy area
    return candidate #, policy_area

def create_json_file(data):
    with open('political_search_results.json', 'w') as f:
        json.dump(data, f, indent=2)

# Function to get embeddings from OctoAI
def get_embedding(text):
    url = f"{OPENAI_BASE_URL}/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OCTOAI_API_KEY}"
    }
    payload = {
        "input": [text],
        "model": "thenlper/gte-large"   
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['data'][0]['embedding']
    else:
        raise Exception(f"Failed to get embedding: {response.text}")

if __name__ == '__main__':
    results = []
    for query in queries:
        response_data = get_serper_api_results(query)
        
        summary = get_summary(query)
        candidate = extract_info_from_query(query)

        # Generate a unique ID for this entry
        # unique_id = str(uuid.uuid4())
        
        # # Prepare the metadata
        # metadata = {
        #     "candidate": candidate,
        #     "policy_area": policy_area,
        #     "links": get_top_3_links_with_metadata(response_data)
        # }
        
        # # Add to the appropriate collection based on the candidate
        # if candidate == "Donald Trump":
        #     collection_red.add(
        #         embeddings=[get_embedding(summary)],
        #         metadatas=[metadata],
        #         ids=[unique_id]
        #     )
        # else:  # Joe Biden
        #     collection_blue.add(
        #         embeddings=[get_embedding(summary)],
        #         metadatas=[metadata],
        #         ids=[unique_id]
        #     )
        
        # print(f"Added entry for {candidate} on {policy_area} to Chroma DB")

        
        result = {
            "candidate": candidate,
            # "policy_area": policy_area,
            "content": summary,
            "metadata": get_top_3_links_with_metadata(response_data)
        }
        # if candidate == "Donald Trump":
        #     collection_red.add(
        #         embeddings=[get_embedding(summary)],
        #         metadatas=[{"chapter": "3", "verse": "16"}, {"chapter": "3", "verse": "5"}, {"chapter": "29", "verse": "11"}, ...],
        #         ids=["id1", "id2", "id3", ...]
        #     )
        # else:
        #     collection_red.add(
        #         embeddings=[get_embedding(summary)],
        #         metadatas=[get_top_3_links_with_metadata(response_data)],
        #         ids=["id1", "id2", "id3", ...]
        #     )

        results.append(result)
    
    create_json_file(results)
    print("JSON file created: political_search_results.json")