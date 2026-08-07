from app.prompts.system_prompt import SYSTEM_PROMPT


class ConversationManager:

    def __init__(self):

        self.history = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }

        ]

    def add_user_message(self, text):

        self.history.append(

            {
                "role": "user",
                "content": text
            }

        )

        self.trim()

    def add_assistant_message(self, text):

        self.history.append(

            {
                "role": "assistant",
                "content": text
            }

        )

        self.trim()

    def get_messages(self):

        return self.history

    def trim(self):

        if len(self.history) > 11:

            self.history = [

                self.history[0]

            ] + self.history[-10:]