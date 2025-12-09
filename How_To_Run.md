# How to run

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

