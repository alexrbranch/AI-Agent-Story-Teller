import os
import json
import logging
import time
from openai import OpenAI
from dotenv import load_dotenv


import configs
import schemas

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

"""

# Simple logger: root config only
logging.basicConfig(level=logging.INFO, filename=configs.LOG_FILE)
logger = logging.getLogger("Storyteller")

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Agent:
    def __init__(self, role_name, system_prompt, model=configs.MODEL_NAME, response_schema=None):
        self.role = role_name
        self.system_prompt = system_prompt
        self.model = model
        self.response_schema = response_schema
        
    def call_model(self, prompt: str, max_tokens=3000, temperature=0.5) -> str:
        print(f"[{self.role}] Thinking...")

        # Ensure prompt is a string the API accepts
        if hasattr(prompt, "model_dump_json"):
            user_content = prompt.model_dump_json()
        elif isinstance(prompt, dict):
            user_content = json.dumps(prompt)
        else:
            user_content = str(prompt)

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]

        request_args = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        # convert pydantic schema to OpenAI tool schema
        if self.response_schema:
            tool_schema = {
                "type": "function",
                "function": {
                    "name": "provide_output",
                    "description": f"Output the data for {self.role}",
                    "parameters": self.response_schema.model_json_schema()
                }
            }
            request_args["tools"] = [tool_schema]
            request_args["tool_choice"] = {"type": "function", "function": {"name": "provide_output"}}

        resp = client.chat.completions.create(**request_args)

        # If no pydantic schema, just return the content
        if not self.response_schema:
            content = resp.choices[0].message.content
            logger.info(f"[{self.role}] Response: \n{content}")
            return content


        # otherwise, parse the tool call arguments into a pydantic object
        tools_args = resp.choices[0].message.tool_calls[0].function.arguments

        pydantic_data = self.response_schema.model_validate_json(tools_args)
        logger.info(f"[{self.role}] Pydantic Output: \n{pydantic_data}")

        return pydantic_data

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


# Logic loop for the outline improvement
def outliner_flow(user_request):
    outliner = Agent(role_name="Outliner", system_prompt=configs.OUTLINER_SYSTEM_PROMPT, response_schema=schemas.StoryOutline)
    editor = Agent(role_name="Outline Editor", system_prompt=configs.EDITOR_SYSTEM_PROMPT, response_schema=schemas.Critique)

    iterations = 0
    current_task = user_request
    # Improvement loop
    while iterations < configs.MAX_ITERATIONS:
        iterations += 1
        print(current_task)
        # Generate outline
        outline = outliner.call_model(user_request)
        # Edit the outline
        judge_input = f"Evaluate this outline for safety/logic: {outline.model_dump_json()}"
        critique = editor.call_model(judge_input, temperature=configs.TEMPERATURE_EDITOR)

        # Editor decideds what to do next
        if critique.approved:
            logger.info(f"Outline APPROVED after {iterations} iterations")
            return outline
        else:
            logger.info(f"Outline REJECTED on {iterations} iteration")
            current_task = (
                f"Previous Rejected Outline: {outline.model_dump_json()}\n",
                f"Critique: {critique.critique_text}\n",
                f"Original User Request: {user_request}\n",
            )

    logger.info(f"Max iterations reached. Returning last rejected outline.")
    return current_task[0]
        



def main():
    start_time = time.time()
    logger.info(f"\n\n\n\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting storyteller...")

    name, theme = get_user_inputs()
    user_request = f"Create a story about {theme} with the main character {name}."

    outline_refined = outliner_flow(user_request)

    storyteller = Agent(role_name="Storyteller", system_prompt=configs.WRITER_SYSTEM_PROMPT)
    story_content = storyteller.call_model(outline_refined)

    judge = Agent(role_name="Judge", system_prompt=configs.JUDGE_SYSTEM_PROMPT)
    judge_result = judge.call_model(story_content)
    
    save_story(story_content + "\n\n" + judge_result)


if __name__ == "__main__":
    main()