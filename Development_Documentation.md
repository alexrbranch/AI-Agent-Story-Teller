1. Skeleton code used and old API which is no longer supported. Updated to use [ChatCompletions API](https://platform.openai.com/docs/api-reference/chat). Opted for this instead of Responses because it doesnt abstract away some of the state management.

2. Modularized the agent construction. Created a class to spin up new agents with unique systems prompts and temperatures. 

3. Request user inputs for a story theme and the name of the main character. A single storyteller agent outputs a typical story with a "once upon a time" introduction. Typical story, not much creativity/variety.

4. Added an outliner agent. Tested independently to validate the json output of the story structure. The storyteller handles the json outline well and produces a well structured story.

5. Added logging to save agent outputs for debugging later.

6. A judge now reviews the story at the very end and provides metrics for letter grade, age suitability, vocabulary analysis, critiques, and if the story is kid-safe.

7. Use pydantic for type enforcement. This, with openai tools, will give a structural guarantee of each agent's output to make flow more deterministic. (Also dont need to include JSON requesting in system prompts as its now forced)

8. Built outliner loop to agenticly improve the outline. Added a max iterations of 3 and a low temperature on the editor to encourage objective feedback. With each iteration, send back the rejected outline, critique, and the user's story request. The outline editor accepts almost every outline. Need to make it more critical. Forcing denial every time lets the outline iterate MAX_RETRIES times.

9. Modularized the feedback loop function to be useable by story editor. Added story critic and some more customs schemas for critics, story.

10. Added an idea generation agents to create 3 separate ideas based on the theme. This lets the user define their ideal story.

OBERSERVATIONS:
The final judge gave increasingly better letter grades as I created more feedback loops. The outline and story were more refined.