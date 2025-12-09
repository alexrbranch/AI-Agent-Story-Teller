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


# Logic loop for the feedback improvement. Works for both outline and story.
def feedback_loop(generator_agent, judge_agent, initial_prompt):
    
    iterations = 0
    current_task = initial_prompt
    # Improvement loop
    while iterations < configs.MAX_ITERATIONS:
        iterations += 1

        # Generate the content
        content = generator_agent.call_model(current_task)

        # Critic the content
        critic_input = f"Review this: {content.model_dump_json()}"
        critique = judge_agent.call_model(critic_input, temperature=0.0)

        # Editor decideds what to do next
        if critique.approved:
            logger.info(f"{generator_agent.role} APPROVED after {iterations} iterations")
            return content
        else:
            logger.info(f"{generator_agent.role} REJECTED on {iterations} iteration")
            current_task = (
                f"Previous Rejected Outline: {content.model_dump_json()}\n",
                f"Critique: {critique.critique_text}\n",
                f"Original prompt: {initial_prompt}\n",
            )

    logger.info(f"Max iterations reached. Returning last rejected outline.")
    return current_task[0]


def main():
    logger.info(f"\n\n\n\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting storyteller...")

    theme, name = get_user_inputs()

    idea_agent = Agent(role_name="Idea Generator", system_prompt=configs.IDEA_SYSTEM_PROMPT, response_schema=schemas.IdeaList)
    prompt = f"Generate 3 story ideas which MUST be based on the theme: '{theme}'."
    idea_list = idea_agent.call_model(prompt, temperature=0.8) # higher temperature for creativity
    logging.info(f"Idea List: {idea_list.model_dump_json()}")


    print("\n--- SELECT A STORY CONCEPT ---")
    for i, idea in enumerate(idea_list.ideas):
        print(f"{i+1}. {idea.summary}")
    
    choice = input(f"\nSelect Number (1-{len(idea_list.ideas)}): ")
    try:
        selected_idea = idea_list.ideas[int(choice)-1]
    except:
        print("Invalid selection. Defaulting to idea 1")
        selected_idea = idea_list.ideas[0]

    user_request = f"Create an outline for the story summarized here: {selected_idea.summary} with a main character named {name}."

    # OUTLINE FEEDBACK LOOP
    outliner = Agent(role_name="Outliner", system_prompt=configs.OUTLINER_SYSTEM_PROMPT, response_schema=schemas.StoryOutline)
    outline_editor = Agent(role_name="Outline Editor", system_prompt=configs.OUTLINE_EDITOR_SYSTEM_PROMPT, response_schema=schemas.Critique)
    outline_refined = feedback_loop(outliner, outline_editor, user_request)

    # STORY FEEDBACK LOOP
    storyteller = Agent(role_name="Storyteller", system_prompt=configs.WRITER_SYSTEM_PROMPT, response_schema=schemas.StoryDraft)
    story_editor = Agent(role_name="Story Editor", system_prompt=configs.STORY_EDITOR_SYSTEM_PROMPT, response_schema=schemas.Critique)
    story_content = feedback_loop(storyteller, story_editor, outline_refined.model_dump_json())

    # FINAL JUDGE TO ASSIGN A LETTER GRADE AND FINAL FEEDBACK
    judge = Agent(role_name="Judge", system_prompt=configs.JUDGE_SYSTEM_PROMPT, response_schema=schemas.StoryGrade)
    judge_result = judge.call_model(story_content)
    
    save_story("Title: " + story_content.title + "\n" + story_content.content + "\n\n" + judge_result.model_dump_json())


if __name__ == "__main__":
    main()