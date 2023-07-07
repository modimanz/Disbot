import openai
import settings

openai.api_key = settings.openai_key


class ChatBot:
    def __init__(self):
        self.chat_history = {}
        self.attitude_default_prompt = "You are an annoyed and contrary assistant. with a punk attitude."
        self.user_attitudes = {}
        self.temperature_default = 0.9
        self.user_temperatures = {}

    def generate_response(self, user_id, message):
        # Add the user's input to the conversation history
        # self.conversation_history.append(f"User: {user_input}\n")

        chat_history = self.chat_history.get(user_id, [])

        attitude_prompt = self.user_attitudes.get(user_id, self.attitude_default_prompt)
        temperature = self.user_temperatures.get(user_id, self.temperature_default)

        # Combine the conversation history, attitude prompt and user's input into one string
        # prompt = "".join(self.conversation_history) + self.attitude_prompt + "\n%s" % user_input

        prompt = [{'role': 'system', 'content': attitude_prompt}]

        for m in chat_history:
            prompt.append(m)
        prompt.append({'role': 'user', 'content': message})

        print("Prompt: %s" % prompt)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # "text-davinci-003",
            messages=prompt,
            max_tokens=1000,
            # n=1,
            # stop=None,
            temperature=temperature,
        )

        assistant_message = response.choices[0]['message']['content']

        # Add the model's output to the conversation history
        self.chat_history[user_id] = chat_history + [{'role': 'user', 'content': message}, {'role': 'assistant', 'content': assistant_message}]

        return assistant_message

    def set_attitude(self, user_id, attitude_prompt):
        # Set the user-specific attitude prompt
        self.user_attitudes[user_id] = attitude_prompt

    def set_temperature(self, user_id, temperature):
        # Set the user-specific temperature
        self.user_temperatures[user_id] = temperature


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
