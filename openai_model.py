import os
import openai

openai.organization = os.environ.get("ORGANIZATION")
openai.api_key = os.environ.get("OPEN_AI_KEY")


def gpt35model(prompt):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": "I am a smart programmer and developper"},            
            {"role": "assistant", "content": "Provide accurate technical answers on technology only"},
            {"role": "user", "content": prompt}     
            ],
        temperature=0.2,         
        # max_tokens=50,  # Adjust max output tokens as needed
        stream=False
        )

    return completion.choices[0].message.content

if __name__ == "__main__":
    print("===================")
    question = "linux command for recursive folder copy"
    completion = gpt35model(question)
    print(completion)  
    print("===================")
    question = "translate 'how are you' to french"
    completion = gpt35model(question)
    print(completion)   
    print("===================")
    question = "Python code for factorial"
    completion = gpt35model(question)
    print(completion)   
    print("===================")
    question = "give me financial advice"
    completion = gpt35model(question)
    print(completion)   
    print("===================")
    question = "common cold and covid"
    completion = gpt35model(question)
    print(completion)   
    print("===================")
    question = "write a poem about philosophy"
    completion = gpt35model(question)
    print(completion)    
    print("===================")
    question = "what is 5 + 6 * 30"
    completion = gpt35model(question)
    print(completion)  
    print("===================")
    question = "write a biography about gadaffi"
    completion = gpt35model(question)
    print(completion)  
    print("===================")
    question = "what questions can you answer"
    completion = gpt35model(question)
    print(completion)  
    print("===================")
    question = "tell me a joke"
    completion = gpt35model(question)
    print(completion)  