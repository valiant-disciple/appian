from groq import Groq
import os 

client = Groq(api_key="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")

def generate_completion(prompt): 
    chat_completion = client.chat.completions.create( messages=[ { "role": "user", "content": prompt, } ], model="llama3-8b-8192", ) 
    if hasattr(chat_completion, 'content'): 
        return str(chat_completion.content) 
    elif hasattr(chat_completion, 'choices'): 
        return str(chat_completion.choices[0].message.content) 
    else: 
        return str(chat_completion)
    
print(generate_completion("Hi"))