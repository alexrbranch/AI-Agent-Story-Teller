import os
from openai import OpenAI
from dotenv import load_dotenv
import configs

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

"""

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Agent:
    def __init__(self, role_name, system_prompt, model: configs.MODEL_NAME):
        self.role = role_name
        self.system_prompt = system_prompt
        self.model = model

    def call_model(self, prompt: str, max_tokens=3000, temperature=0.5) -> str:
        print(f"[{self.role}] Thinking...")

        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content

def get_user_inputs():
    print("Welcome to this storyteller. Please provide a theme for this story.")
    input_theme = input("Theme: ")
    print("What should we name the main character? (You can make yourself the hero!)")
    input_character_name = input("Character Name: ")

    return input_theme, input_character_name


def main():
    name, theme = get_user_inputs()

    storyteller = Agent(role_name="Storyteller", system_prompt=configs.WRITER_SYSTEM_PROMPT, model=configs.MODEL_NAME)

    response = storyteller.call_model(f"Create a story about {theme} with the main character {name}.")
    print(response)


if __name__ == "__main__":
    main()