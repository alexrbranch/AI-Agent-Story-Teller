1. Skeleton code used and old API which is no longer supported. Updated to use [ChatCompletions API](https://platform.openai.com/docs/api-reference/chat). Opted for this instead of Responses because it doesnt abstract away some of the state management.

2. Modularized the agent construction. Created a class to spin up new agents with unique systems prompts and temperatures. 

3. Request user inputs for a story theme and the name of the main character. A single storyteller agent outputs a typical story with a "once upon a time" introduction. Typical story, not much creativity/variety.