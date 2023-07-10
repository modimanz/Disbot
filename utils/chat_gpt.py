import openai
import settings
import utils.attitudes as attitudes
import re
import random

openai.api_key = settings.openai_key

# global token counts
input_token_count = 0  # load_token_count('input_token_count.txt')
output_token_count = 0  # load_token_count('output_token_count.txt')
input_token_file = 'input_tokens.txt'
output_token_file = 'output_tokens.txt'


# TODO Turn this in a Tokens class
def estimate_tokens(message, filename):
    if isinstance(message, list):
        count = sum(len(re.split(r'\s|-', msg['content'])) for msg in message)
    else:
        count = len(re.split(r'\s|-', message))
    update_token_count(filename, count)
    return count


def estimate_input_tokens(message):
    return estimate_tokens(message, input_token_file)


def estimate_output_tokens(message):
    return estimate_tokens(message, output_token_file)


def update_token_count(filename, count):
    global input_token_count
    global output_token_count

    if filename == input_token_file:
        input_token_count += count
        with open(filename, 'w') as f:
            f.write(str(input_token_count))
    elif filename == output_token_file:
        output_token_count += count
        with open(filename, 'w') as f:
            f.write(str(output_token_count))


def load_token_count(filename):
    try:
        with open(filename, 'r') as f:
            return int(f.read().strip())
    except FileNotFoundError:
        print(f"{filename} not found. Initializing token count to 0.")
        return 0


class ChatBot:
    def __init__(self):
        global input_token_count, output_token_count
        self.chat_history = {}
        self.attitude_default_prompt = attitudes.choose_attitude()
        # "You are an annoyed and contrary assistant. with a punk attitude."
        self.user_attitudes = {}
        self.temperature_default = 0.9
        self.user_temperatures = {}
        input_token_count = load_token_count(input_token_file)
        output_token_count = load_token_count(output_token_file)
        self.topic_starters = []
        self.topic_starter = ""

    def generate_response(self, user_id, message):
        # Add the user's input to the conversation history
        # self.conversation_history.append(f"User: {user_input}\n")

        if user_id != 0:
            chat_history = self.chat_history.get(user_id, [])
        else:
            chat_history = []

        attitude_prompt = self.user_attitudes.get(user_id, attitudes.choose_attitude())
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
            max_tokens=2000,
            # n=1,
            # stop=None,
            temperature=temperature,
        )

        estimate_input_tokens(prompt)
        estimate_output_tokens(response.choices[0]['message']['content'])

        assistant_message = response.choices[0]['message']['content']

        # Add the model's output to the conversation history
        self.chat_history[user_id] = chat_history + [{'role': 'user', 'content': message},
                                                     {'role': 'assistant', 'content': assistant_message}]

        return assistant_message

    def set_attitude(self, user_id, attitude_prompt=None):
        if attitude_prompt is None:
            attitude_prompt = attitudes.choose_attitude()
        # Set the user-specific attitude prompt
        self.user_attitudes[user_id] = attitude_prompt

    def set_temperature(self, user_id, temperature):
        # Set the user-specific temperature
        self.user_temperatures[user_id] = temperature

    def generate_topic_starter(self):
        """
        Need to generate a list or random interesting topic starters and choose one
        :return:
        """
        content = self.generate_response(0, "Generate a list of random wierd topic starters related to your attitude.")

        lines = content.split('\n')

        # Only keep lines that start with a number or bullet, and remove the numbering/bullets
        items = [re.sub(r'^[\d\.]*\s*', '', line).strip() for line in lines if re.match(r'^[\d\.]+', line)]

        self.topic_starters = items

        self.topic_starter = random.choice(items)

        response = self.generate_response(0, self.topic_starter)

        return response
        # TODO Add logic here

    async def start_a_conversation(self, ctx):
        response = self.generate_topic_starter()
        await ctx.send(response)


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


"""
TODO Generate lists
"Generate a list of interesting questions about technology."
"Generate a list of conversation starters about recent movies."
"Generate a list of intriguing questions about space exploration."
"Generate a list of thought-provoking philosophical questions."
"Generate a list of fun trivia questions about 90s pop culture."
"Generate a list of engaging questions about famous authors and their works."
"Generate a list of conversation starters about environmental issues."
"Generate a list of thought-provoking questions about artificial intelligence."
"Generate a list of interesting discussion topics about music trends."
"Generate a list of captivating questions about world cultures."
"""
