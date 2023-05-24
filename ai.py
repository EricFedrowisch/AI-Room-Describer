import openai
import asyncio
import os
import glob

openai.api_key_path = "./openai_api_key.txt"

def load_prompts(folder: str):
    # Initialize an empty list for prompts
    prompts = {}
    # Use glob to find all files in the folder that end with .prompt
    for filename in glob.glob(os.path.join(folder, '*.txt')):
        with open(filename, 'r') as file:
            f = filename.split('/')[-1]  # Split file path on '/', get last element
            key = f.split('.')[0]  # Split filename on . and discard "prompt"
            # Read the file and add its contents to the prompts dict
            prompts[key] = file.read()
    return prompts

PROMPTS = load_prompts('./prompts')
# print(PROMPTS.values())

class AI:
    model_list = openai.Model.list()['data']
    model_ids = [x['id'] for x in model_list]

    def __init__(self, prompt='room_description', model="gpt-3.5-turbo"):
        self.prompt_key = prompt
        self.prompt = PROMPTS[self.prompt_key]
        self.model = model

    async def get_response(self, msg):
        self.response = None
        self.last_input = msg
        send=[
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": msg},
        ]
        try:
            raw = openai.ChatCompletion.create(model = self.model, messages=send)
            self.response = Response(raw)
        except Exception as e:
            print(f"[OPENAI] ERROR {e}")
        return self.response


class Response:
    """Convenience Wrapper for openai response dicts"""
    def __init__(self, raw_response: dict):
        self.raw = raw_response
        self.text = self.raw['choices'][0]['message']['content']
    
    def print_raw(self):
        for k, v in self.raw:
            print(f"{k}: {v}")


if __name__ == "__main__":
    ai = AI()  # Create an ai to query
    msg = "A Deep Dark Dungeon"  # Create a message
    # Do the event loop stuff
    event_loop = asyncio.get_event_loop()
    query = event_loop.create_task(ai.get_response(msg))
    event_loop.run_until_complete(query)
    # Query is done
    response = query.result()
    print(response.text)