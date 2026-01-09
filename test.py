import os
from openai import AzureOpenAI

endpoint = "https://ngstc-m8mh44u5-swedencentral.cognitiveservices.azure.com/"
model_name = "o3-mini"
deployment = "o3-mini"

subscription_key = "...."
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "I am going to Paris, what should I see?",
        }
    ],
    max_completion_tokens=100000,
    model=deployment
)

print(response.choices[0].message.content)
