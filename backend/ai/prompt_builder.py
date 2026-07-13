# backend/ai/prompt_builder.py

from ai.logger import logger

def build_prompt(profile_data: dict) -> str:
    """
    Builds an optimized, token-saving prompt using the learner profile questionnaire, 
    career recommendation quiz, and placement profile (if applicable) data.
    Enforces the mandatory inclusion of Git, SQL, APIs, Framework, and Deployment topics.
    """
    logger.info("Building optimized prompt using user profile data")
    
    career = profile_data.get("career", "Software Engineer")
    languages = profile_data.get("languages", "Python, JavaScript")
    skill = profile_data.get("skill", "Beginner")
    study_time = profile_data.get("study_time", "1–2 Hours")
    timeline = profile_data.get("timeline", "6 Months")
    learning_style = profile_data.get("learning_style", "Practical/Project-based")
    year = profile_data.get("year", "1st Year")
    branch = profile_data.get("branch", "Computer Science")

    prompt = f"""Create two learning roadmaps (1. Fast Track: rapid onboarding, core topics; 2. Deep Learning: mastery, fundamental & advanced topics) for:
Goal: {career}
Langs: {languages}
Level: {skill}
Time: {study_time}
Timeline: {timeline}
Style: {learning_style}
Year: {year}
Branch: {branch}
"""

    if profile_data.get("career_quiz_answers"):
        qa = profile_data["career_quiz_answers"]
        prompt += f"\nCareer Recommendation Quiz Answers:\n- Preferred Activities: {qa.get('activities')}\n- Favorite Subject: {qa.get('subject')}\n- Preferred Work Type: {qa.get('work_type')}\n- Recommended Careers: {qa.get('recommended_careers')}\n"

    if profile_data.get("questionnaire_answers"):
        qa = profile_data["questionnaire_answers"]
        prompt += f"\nRoadmap Questionnaire Details:\n- Name: {qa.get('name')}\n- College: {qa.get('college')}\n- Year: {qa.get('year')}\n- Branch: {qa.get('branch')}\n- Target Timeline: {qa.get('timeline')}\n"

    if profile_data.get("placement_answers"):
        pa = profile_data["placement_answers"]
        prompt += f"\nPlacement Profile Details (Applicable):\n- Aptitude Level: {pa.get('aptitude_level')}\n- DSA Level: {pa.get('dsa_level')}\n- Target Companies: {pa.get('target_companies')}\n- Target Timeline: {pa.get('timeline')}\n"

    prompt += """
Must include: Git/GitHub, SQL/Database Design, APIs (REST, lifecycle), Major Framework, Deployment/Testing/CI-CD.
Return JSON matching this schema:
{
  "roadmaps": [
    {
      "title": "Roadmap Title",
      "description": "Short Description",
      "phases": [
        {
          "phase_number": 1,
          "phase_title": "Phase Title",
          "estimated_duration": "Duration (e.g. 2 weeks)",
          "topics": [
            {
              "topic": "Topic Name",
              "difficulty": "Easy/Medium/Hard",
              "estimated_hours": 10,
              "resources": [{"title": "Resource Name", "url": "placeholder_url"}],
              "mini_project": "Short project description",
              "quiz_required": true
            }
          ]
        }
      ]
    }
  ]
}
Ensure all JSON fields are populated. Return JSON only."""
    
    logger.info(f"AI prompt built. Prompt text length: {len(prompt)}")
    return prompt
