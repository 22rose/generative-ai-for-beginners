from openai import AzureOpenAI
import os
import dotenv

# import dotenv
dotenv.load_dotenv()

# configure Azure OpenAI service client 
client = AzureOpenAI(
  azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"], 
  api_key=os.environ['AZURE_OPENAI_API_KEY'],  
  api_version = "2023-10-01-preview"
  )

deployment=os.environ['AZURE_OPENAI_DEPLOYMENT']

hist_fig = input("What historical figure would you like your chatbox to be?: ")
tone = input("What tone would you like your historical figure to have?: ")

prompt = f"I want you to take on the persona of {hist_fig} and answer subsequent questions about the historical figure with this tone: {tone}"
messages = [{"role": "system", "content": prompt}]

while True:  #change this to some limit
    question = input("Ask your historical figure a question: ")
    messages.append({"role": "user", "content": question})
    response = client.chat.completions.create(model=deployment, messages=messages, temperature=0.5, max_tokens = 150)
    output = response.choices[0].message.content
    print(output)