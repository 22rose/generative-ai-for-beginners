import os
from openai import AzureOpenAI

import openai
from dotenv import load_dotenv
load_dotenv()

client = AzureOpenAI(
  api_key=os.environ['AZURE_OPENAI_API_KEY'],  # this is also the default, it can be omitted
  api_version = "2023-05-15"
  )

deployment=os.environ['AZURE_OPENAI_DEPLOYMENT']

# def get_completion(prompt):
#     messages = [{"role": "user", "content": f"Complete the following: {prompt}"}]
#     response = client.chat.completions.create(
#         model=deployment,
#         messages=messages,
#         temperature=0,  # this is the degree of randomness of the model's output
#         max_tokens=1024
#     )
#     return response.choices[0].message.content

# prompt = "Once upon a time there was a"
# completion = get_completion(prompt)
# print(completion)

prompt = "Complete the following: Once upon a time there was a"
messages = [{"role": "user", "content": prompt}]
response = client.chat.completions.create(
    model=deployment,
    messages=messages,
    temperature=0,  # this is the degree of randomness of the model's output
    max_tokens=1024
)
completion = response.choices[0].message.content
print(completion)

