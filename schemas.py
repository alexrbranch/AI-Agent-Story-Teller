from pydantic import BaseModel, Field
from typing import List

class StoryIdea(BaseModel):
    summary: str = Field(description="One sentence summary")

class IdeaList(BaseModel):
    ideas: List[StoryIdea] = Field(description="A list of 3 distinct story concepts")

class StoryOutline(BaseModel):
    title: str = Field(description="The title of the story")
    character_name: str = Field(description="The main character's name")
    theme: str = Field(description="The story theme")
    setup: str = Field(description="Introduction of character and setting")
    incident: str = Field(description="The inciting incident or problem")
    climax: str = Field(description="The peak of the action")
    resolution: str = Field(description="How it ends and the lesson learned by the main character")

class Critique(BaseModel):
    approved: bool = Field(description="Set to True ONLY if the outline is safe and follows logic. False otherwise.")
    critique_text: str = Field(description="Specific feedback on what to do next time for a better story.")
    safety_score: int = Field(description="1-10 safety score, 10 is safest.")

class StoryDraft(BaseModel):
    title: str
    content: str = Field(description="The full story")

class StoryGrade(BaseModel):
    grade: str = Field(description="Letter grade (A-F)")
    age_appropriateness: int = Field(description="1-10 score")
    engagement: int = Field(description="1-10 score")
    final_feedback: str = Field(description="Comments for the author")
