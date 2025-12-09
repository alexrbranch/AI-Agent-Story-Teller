import os
import json
import logging
import time
from openai import OpenAI
from dotenv import load_dotenv


import configs

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

"""

# Simple logger: root config only
logging.basicConfig(level=logging.INFO, filename=configs.LOG_FILE)
logger = logging.getLogger("Storyteller")

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Agent:
    def __init__(self, role_name, system_prompt, model=configs.MODEL_NAME):
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

def save_story(content):
    with open(configs.STORY_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Story saved to {configs.STORY_OUTPUT_FILE}")

def main():
    start_time = time.time()
    logger.info(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting storyteller...")

    name, theme = get_user_inputs()
    user_request = f"Create a story about {theme} with the main character {name}."
    logger.info("User request: \n{user_request}")

    outliner = Agent(role_name="Outliner", system_prompt=configs.OUTLINER_SYSTEM_PROMPT)
    outline_raw = outliner.call_model(user_request) #json output
    logger.info(f"Outline raw: \n{outline_raw}")

    storyteller = Agent(role_name="Storyteller", system_prompt=configs.WRITER_SYSTEM_PROMPT)
    story_content = storyteller.call_model(outline_raw)
    logger.info(f"Story content: \n{story_content}")
    
    save_story(story_content)


if __name__ == "__main__":
    main()