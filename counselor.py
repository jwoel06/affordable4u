from dotenv import load_dotenv
from anthropic import Anthropic

SYSTEM_PROMPT = """ You are a college counselor. You are required to ask enough questions to gather enough context to make 
a recommendation regarding the college the client should go to.
"""

class MyCounselor: 

    def __init__(self):
        self.client = Anthropic()
        self.conversation_history = []

    def counselor_chat(self, user_message):
        self.conversation_history.append({
            "role" : "user",
            "message" : user_message,

        })

        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=self.conversation_history
        )
        
        assistant_message = response.content[0].text
        self.conversation_history.append({
            "role" : "assistant",
            "message" : assistant_message,

        })

        return assistant_message