import openai
import settings

openai.api_key = settings.openai_key


class ChatBot:
    def __init__(self):
        self.conversation_history = []
        self.attitude_prompt = "You are an annoyed and contrary assistant. with a punk attitude."

    def generate_response(self, user_input):
        # Add the user's input to the conversation history
        self.conversation_history.append(f"User: {user_input}\n")

        # Combine the conversation history, attitude prompt and user's input into one string
        prompt = "".join(self.conversation_history) + self.attitude_prompt + "\n%s" % user_input

        print("Prompt: %s" % prompt)

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.5,
        )

        message = response.choices[0].text.strip()

        # Add the model's output to the conversation history
        self.conversation_history.append(f"AI: {message}\n")

        return message


def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = response.choices[0].text.strip()
    return message
