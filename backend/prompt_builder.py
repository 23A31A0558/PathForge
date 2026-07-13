# backend/prompt_builder.py

def build_prompt(profile_data: dict) -> str:
    """
    Builds the personalized prompt for the Groq AI.
    Inputs come from the RoadmapQuestionnaire, Answers, CareerRecommendationQuiz, and PlacementProfile tables.
    """
    template = """You are an expert software engineering mentor and career advisor.

Analyze the following learner profile.

Career Goal:
{career}

Programming Languages:
{languages}

Current Skill Level:
{skill}

Daily Study Time:
{study_time}

Target Timeline:
{timeline}

Learning Style:
{learning_style}

College Year:
{year}

Branch:
{branch}

Generate TWO personalized learning roadmaps.

Roadmap 1

Fast Track

Roadmap 2

Deep Learning

Each roadmap must contain

- Title

- Description

- Learning Phases

- Topics

- Difficulty

- Estimated Hours

- Mini Project

- Free Resources

- Quiz Required

Return ONLY valid JSON.

Never return markdown.
"""
    return template.format(
        career=profile_data.get("career", "Software Engineer"),
        languages=profile_data.get("languages", "Python, JavaScript"),
        skill=profile_data.get("skill", "Beginner"),
        study_time=profile_data.get("study_time", "1-2 Hours"),
        timeline=profile_data.get("timeline", "6 Months"),
        learning_style=profile_data.get("learning_style", "Practical/Project-based"),
        year=profile_data.get("year", "1st Year"),
        branch=profile_data.get("branch", "Computer Science")
    )
