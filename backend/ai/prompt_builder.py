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

def build_placement_prompt(profile_data: dict) -> str:
    """
    Builds a prompt tailored for a Placement Preparation Roadmap.
    Instructs the AI to generate a single, highly personalized placement roadmap
    conforming to the required easy->medium->hard chronological progression.
    """
    logger.info("Building optimized placement prompt using user profile data")
    
    placement_answers = profile_data.get("placement_answers", {})
    name = profile_data.get("questionnaire_answers", {}).get("name", "Explorer") if profile_data.get("questionnaire_answers") else "Explorer"
    college = profile_data.get("questionnaire_answers", {}).get("college", "University") if profile_data.get("questionnaire_answers") else "University"
    
    # Extract placement variables
    aptitude_level = placement_answers.get("aptitude_level", "Beginner")
    dsa_level = placement_answers.get("dsa_level", "Beginner")
    target_companies = placement_answers.get("target_companies", "Infosys, TCS")
    timeline = placement_answers.get("timeline", "6 Months")
    branch = profile_data.get("branch", "Computer Science")
    year = profile_data.get("year", "3rd Year")

    # Personalization instruction based on aptitude
    if aptitude_level == "Beginner":
        aptitude_instruction = (
            "Start from basic aptitude topics: Number System, Percentages, Ratio & Proportion, "
            "Profit & Loss, Time & Work, Time Speed Distance, Simple & Compound Interest, Logical Reasoning Basics."
        )
    elif aptitude_level == "Intermediate":
        aptitude_instruction = (
            "Skip beginner aptitude topics. Start from intermediate aptitude topics: "
            "Probability, Permutations, Combinations, Data Interpretation, Puzzles, Advanced Reasoning."
        )
    else: # Advanced
        aptitude_instruction = (
            "Focus on advanced aptitude topics: Mixed Mock Tests, Company Aptitude, Speed Improvement."
        )

    # Personalization instruction based on DSA
    if dsa_level == "Beginner":
        dsa_instruction = (
            "Generate basic DSA topics: Arrays, Strings, Sorting, Searching, Recursion, Basic Mathematics, Basic Hashing."
        )
    elif dsa_level == "Intermediate":
        dsa_instruction = (
            "Generate intermediate DSA topics: Linked Lists, Stacks, Queues, Trees, BST, Binary Search, Sliding Window, Two Pointer."
        )
    else: # Advanced
        dsa_instruction = (
            "Generate advanced DSA topics: Graphs, Dynamic Programming, Greedy, Trie, Heap, Segment Tree, Advanced Graph Algorithms, Competitive Coding."
        )

    # Company selection focus
    companies_list = [c.strip().lower() for c in target_companies.split(",")]
    
    product_companies = ["google", "amazon", "microsoft", "apple", "meta", "netflix"]
    service_companies = ["infosys", "tcs", "wipro", "accenture", "capgemini", "cognizant", "deloitte", "ibm"]
    
    product_tier = any(c in product_companies for c in companies_list)
    service_tier = any(c in service_companies for c in companies_list)
    
    company_emphasis = ""
    if product_tier:
        company_emphasis += "Prioritize Google/Amazon/Microsoft/Apple/Meta/Netflix expectations: Hard DSA, Graphs, DP, System Design Basics, Advanced Coding, Mock Interviews. "
    if service_tier:
        company_emphasis += "Prioritize Infosys/TCS/Wipro/Accenture/Capgemini/Cognizant/Deloitte/IBM expectations: Aptitude, SQL, OOP, Basic DSA, HR Interview, Resume. "

    # Timeline adjustment
    if timeline == "3 Months":
        timeline_instruction = "Generate a Fast-track roadmap (3 months duration) focusing on highly critical placement topics."
    elif timeline == "6 Months":
        timeline_instruction = "Generate a Balanced roadmap (6 months duration) covering the complete placement syllabus with adequate practice."
    else: # 1 Year
        timeline_instruction = "Generate a Comprehensive roadmap (1 year duration) for deep-dive, complete placement foundation building."

    prompt = f"""You are an expert technical placement coach. Generate a single, highly personalized **Placement Preparation Roadmap** for a student with the following profile:
- Year of Study: {year}
- Academic Branch: {branch}
- Target Companies: {target_companies}
- Preparation Timeline: {timeline}
- Current Aptitude Level: {aptitude_level}
- Current DSA Level: {dsa_level}

### Structuring Requirements:
1. The roadmap MUST progress strictly from EASY to MEDIUM to HARD difficulty.
2. The roadmap MUST have exactly 4 phases in chronological learning order:
   - **Phase 1: Foundation** (Aptitude focus: {aptitude_instruction}; DSA focus: {dsa_instruction})
   - **Phase 2: Intermediate** (Transition to intermediate topics, data structures, and reasoning)
   - **Phase 3: Advanced** (Cover advanced algorithms, system design basics, advanced SQL as appropriate for target companies)
   - **Phase 4: Interview Preparation** (Cover: Company-wise Coding, Mock Interviews, Resume Building, HR Questions, Technical Interviews, Revision)
3. Incorporate these company-specific emphases: {company_emphasis}
4. Distribute topics realistically across the timeline: {timeline_instruction}

### Important:
Return the roadmap in JSON format matching the schema below. Note that the schema expects a list of roadmaps; please return a list containing exactly **one** roadmap of title "Placement Preparation Roadmap".
Ensure all fields are fully populated (do not use placeholders). Every topic must include valid, relevant curated learning resource titles and urls.

JSON Schema format:
{{
  "roadmaps": [
    {{
      "title": "Placement Preparation Roadmap",
      "description": "Personalized placement prep roadmap targeting {target_companies} in {timeline}.",
      "phases": [
        {{
          "phase_number": 1,
          "phase_title": "Phase Title",
          "estimated_duration": "Duration (e.g. 2 weeks)",
          "topics": [
            {{
              "topic": "Topic Name",
              "difficulty": "Easy/Medium/Hard",
              "estimated_hours": 10,
              "resources": [
                {{
                  "title": "Resource Name",
                  "url": "https://example.com/resource"
                }}
              ],
              "mini_project": "Mini challenge or project",
              "quiz_required": true
            }}
          ]
        }}
      ]
    }}
  ]
}}
Ensure you ONLY return the valid JSON object, without any explanation or markdown formatting."""
    return prompt

