## AI Agent Story teller
Thank you for this opportunity and I hope to hear back soon.

I built an agent storyteller with two generator-critic systems. 

The first builds an outline for the story. 
The second is the prose system.

This structure separated the tasks so an older model like gpt3.5-turbo wont get overwhelmed by having to generate an entire story from scratch. In my testing with single vs multiagent, I found the story quality was much better when provided a detailed outline.

There is also an agent that generates 3 story ideas to give the user input on their bedtime story.

At the end of the script, I attached a judge which scores the essay with a letter grade and provides a short review.

## How to run

1) Ensure you Python 3.10+  
   `python3 --version`  

2) Create and activate a virtual environment
     ```
     python3 -m venv venv
     source venv/bin/activate
     ```

3) Install dependencies
   ```
   pip install -r requirements.txt
   ```

4) Set your OpenAI API key (required)
   Create a `.env` file in the project root with:  
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

5) Run the storyteller
   ```
   python main.py
   ```

Outputs:
- The generated story is saved to `story.txt`.
- Logs go to `system.log`.
- Console prompts will ask for a theme, a character name, and to pick from generated ideas.


