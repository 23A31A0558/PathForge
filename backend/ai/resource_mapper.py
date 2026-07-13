# backend/ai/resource_mapper.py

from ai.logger import logger

CURATED_RESOURCES = {
    "git": [
        {"title": "Git & GitHub Complete Course", "url": "https://www.youtube.com/watch?v=RGOj5yH7evk"},
        {"title": "Git Documentation", "url": "https://git-scm.com/doc"}
    ],
    "sql": [
        {"title": "W3Schools SQL Tutorial", "url": "https://www.w3schools.com/sql/"},
        {"title": "freeCodeCamp SQL & Databases Course", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY"}
    ],
    "database": [
        {"title": "Database Design & Modeling Tutorial", "url": "https://www.youtube.com/watch?v=ztHopE5Wubs"},
        {"title": "SQL Database Basics", "url": "https://www.w3schools.com/sql/"}
    ],
    "html": [
        {"title": "MDN Web Docs - HTML Basics", "url": "https://developer.mozilla.org/en-US/docs/Learn/HTML"},
        {"title": "freeCodeCamp HTML Full Course", "url": "https://www.youtube.com/watch?v=ok-plXXH5nM"}
    ],
    "css": [
        {"title": "MDN Web Docs - CSS Basics", "url": "https://developer.mozilla.org/en-US/docs/Learn/CSS"},
        {"title": "CSS Diner - Flexbox Practice", "url": "https://flukeout.github.io/"}
    ],
    "javascript": [
        {"title": "MDN JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"},
        {"title": "Modern JavaScript ES6+ Course", "url": "https://www.youtube.com/watch?v=d51vODW0cBA"}
    ],
    "react": [
        {"title": "React Official Documentation", "url": "https://react.dev/learn"},
        {"title": "React JS Tutorial for Beginners", "url": "https://www.youtube.com/watch?v=w7ejDZ8SWv8"}
    ],
    "python": [
        {"title": "Python Official Tutorial", "url": "https://docs.python.org/3/tutorial/index.html"},
        {"title": "Real Python Tutorials", "url": "https://realpython.com/"}
    ],
    "pandas": [
        {"title": "Pandas 10-Minute Guide", "url": "https://pandas.pydata.org/docs/user_guide/10min.html"}
    ],
    "matplotlib": [
        {"title": "Matplotlib Quickstart Guide", "url": "https://matplotlib.org/stable/tutorials/introductory/quickstart.html"}
    ],
    "scikit": [
        {"title": "Scikit-Learn Tutorial", "url": "https://scikit-learn.org/stable/tutorial/basic/tutorial.html"}
    ],
    "neural": [
        {"title": "Neural Networks Basics", "url": "https://www.deeplearning.ai/resources/what-is-a-neural-network/"}
    ],
    "fastapi": [
        {"title": "FastAPI Official Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/"}
    ],
    "django": [
        {"title": "Django Girls Tutorial", "url": "https://tutorial.djangogirls.org/"}
    ],
    "node": [
        {"title": "Node.js Official Getting Started", "url": "https://nodejs.org/en/docs/guides/getting-started-guide/"}
    ],
    "security": [
        {"title": "OWASP Top 10 Vulnerabilities", "url": "https://owasp.org/www-project-top-ten/"}
    ],
    "devops": [
        {"title": "Roadmap.sh DevOps Journey", "url": "https://roadmap.sh/devops"}
    ],
    "docker": [
        {"title": "Docker Orientation and Setup", "url": "https://docs.docker.com/get-started/"}
    ],
    "aws": [
        {"title": "AWS Cloud Practitioner Essentials", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/"}
    ],
    "figma": [
        {"title": "Figma Getting Started Guide", "url": "https://help.figma.com/hc/en-us/articles/360040328273-Get-started-with-Figma"}
    ]
}

def map_resources_for_topics(validated_data: dict) -> dict:
    """
    Iterates through topics in the roadmap. Replaces placeholder URLs with
    verified high-quality curated learning links when keywords match.
    Prevents AI from inventing fake URLs.
    """
    logger.info("Normalizing and mapping resource URLs for topics")
    mapped_count = 0
    
    for roadmap in validated_data["roadmaps"]:
        for phase in roadmap["phases"]:
            for topic in phase["topics"]:
                topic_title_lower = topic["topic"].lower()
                mapped = False
                
                # Try to find a curated resource keyword match
                for key, curated in CURATED_RESOURCES.items():
                    if key in topic_title_lower:
                        topic["resources"] = curated
                        mapped = True
                        mapped_count += 1
                        break
                
                # If no keyword match, normalize placeholders to safe GFG or MDN search queries
                if not mapped:
                    for resource in topic["resources"]:
                        url = resource.get("url", "").lower()
                        # Replace if the URL is empty or matches typical invented placeholders
                        trusted_domains = [
                            "developer.mozilla.org", "geeksforgeeks.org", "w3schools.com", 
                            "freecodecamp.org", "github.com", "youtube.com", "react.dev", 
                            "python.org", "oracle.com", "baeldung.com", "spring.io", 
                            "microsoft.com", "git-scm.com", "w3.org", "wikipedia.org"
                        ]
                        if not any(trusted in url for trusted in trusted_domains):
                            query = topic["topic"].replace(" ", "+")
                            resource["url"] = f"https://www.geeksforgeeks.org/search/?q={query}"
                            resource["title"] = f"GeeksforGeeks - {topic['topic']} Guide"
                            mapped_count += 1

                            
    logger.info(f"Finished resource mapping. Updated resources for {mapped_count} items.")
    return validated_data
