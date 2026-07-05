import models

RESOURCE_LINKS = {
    # Frontend
    "HTML/CSS": "https://developer.mozilla.org/en-US/docs/Learn",
    "JavaScript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
    "Bootstrap": "https://getbootstrap.com/docs/5.3/getting-started/introduction/",
    "Figma basics": "https://help.figma.com/hc/en-us/articles/360040328273-Get-started-with-Figma",
    "Components": "https://react.dev/learn/your-first-component",
    "State Management": "https://react.dev/learn/managing-state",
    
    # AI / Data Science
    "Syntax & Variables": "https://docs.python.org/3/tutorial/introduction.html",
    "Functions & Classes": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions",
    "Pandas": "https://pandas.pydata.org/docs/user_guide/10min.html",
    "Matplotlib": "https://matplotlib.org/stable/tutorials/introductory/quickstart.html",
    "Scikit-Learn": "https://scikit-learn.org/stable/tutorial/basic/tutorial.html",
    "Neural Networks Basics": "https://www.deeplearning.ai/resources/what-is-a-neural-network/",
    
    # Backend
    "Variables": "https://realpython.com/python-variables/",
    "Loops": "https://realpython.com/python-while-loop/",
    "Functions": "https://realpython.com/defining-your-own-python-function/",
    "Databases": "https://www.w3schools.com/sql/",
    "FastAPI/Django": "https://fastapi.tiangolo.com/tutorial/",
    "Routing": "https://fastapi.tiangolo.com/tutorial/bigger-applications/",
    "Build API": "https://fastapi.tiangolo.com/tutorial/first-steps/"
}

def generate_roadmaps_for_user(db, user_id):
    # Fetch user answers to determine rule
    answers = db.query(models.Answer).filter(models.Answer.user_id == user_id).all()
    
    role = "backend"  # default rule
    for ans in answers:
        q = db.query(models.Question).filter(models.Question.id == ans.question_id).first()
        if q and q.question_text == "Preferred role":
            role = ans.selected_option
            
    if role == "frontend":
        domain_title = "Frontend Developer"
        macros = ["Basics", "UI Design", "Frameworks (React)"]
        micro_dict = {
            "Basics": [("HTML/CSS", "Learn the web structure", "easy", 5), ("JavaScript", "Learn interactivity", "medium", 10)],
            "UI Design": [("Bootstrap", "Styling library", "easy", 5), ("Figma basics", "Design basics", "easy", 5)],
            "Frameworks (React)": [("Components", "React basics", "medium", 10), ("State Management", "Redux/Context", "hard", 20)]
        }
    elif role == "ai":
        domain_title = "AI/Data Scientist"
        macros = ["Python Basics", "Data Analysis", "Machine Learning"]
        micro_dict = {
            "Python Basics": [("Syntax & Variables", "Learn Python syntax", "easy", 5), ("Functions & Classes", "OOP", "medium", 10)],
            "Data Analysis": [("Pandas", "Data manipulation", "medium", 15), ("Matplotlib", "Visualization", "medium", 10)],
            "Machine Learning": [("Scikit-Learn", "Standard ML", "hard", 20), ("Neural Networks Basics", "Deep Learning intro", "hard", 25)]
        }
    else: # backend or not_sure
        domain_title = "Backend Developer"
        macros = ["Basics", "Core Concepts", "Frameworks", "Projects"]
        micro_dict = {
            "Basics": [("Variables", "Data types and variables", "easy", 5), ("Loops", "For and while loops", "easy", 5)],
            "Core Concepts": [("Functions", "Reusable code blocks", "medium", 10), ("Databases", "SQL Basics", "medium", 15)],
            "Frameworks": [("FastAPI/Django", "Learn a web framework", "hard", 20), ("Routing", "API Routing", "medium", 15)],
            "Projects": [("Build API", "Build a REST API", "hard", 25)]
        }
        
    roadmap_types = [
        {"type": "fast_track", "title": f"Fast-Track: {domain_title}"},
        {"type": "deep_learning", "title": f"Deep-Learning: {domain_title}"}
    ]
    
    # Check if roadmaps already exist and delete to recreate
    existing_roadmaps = db.query(models.Roadmap).filter(models.Roadmap.user_id == user_id).all()
    if existing_roadmaps:
        for r in existing_roadmaps:
            macros_existing = db.query(models.MacroStep).filter(models.MacroStep.roadmap_id == r.id).all()
            for me in macros_existing:
                micros_existing = db.query(models.MicroStep).filter(models.MicroStep.macro_step_id == me.id).all()
                for ms in micros_existing:
                    quizzes = db.query(models.Quiz).filter(models.Quiz.micro_step_id == ms.id).all()
                    for qz in quizzes:
                        db.query(models.QuizQuestion).filter(models.QuizQuestion.quiz_id == qz.id).delete()
                    db.query(models.Quiz).filter(models.Quiz.micro_step_id == ms.id).delete()
                    db.query(models.QuizAttempt).filter(models.QuizAttempt.micro_step_id == ms.id).delete()
                db.query(models.MicroStep).filter(models.MicroStep.macro_step_id == me.id).delete()
            db.query(models.MacroStep).filter(models.MacroStep.roadmap_id == r.id).delete()
        db.query(models.Roadmap).filter(models.Roadmap.user_id == user_id).delete()
        db.commit()

    generated_ids = []
    
    for rt in roadmap_types:
        new_rm = models.Roadmap(user_id=user_id, title=rt["title"], type=rt["type"])
        db.add(new_rm)
        db.commit()
        db.refresh(new_rm)
        generated_ids.append(new_rm.id)
        
        # Build Macros
        for i, m_title in enumerate(macros):
            new_macro = models.MacroStep(roadmap_id=new_rm.id, title=m_title, order_index=i+1)
            db.add(new_macro)
            db.commit()
            db.refresh(new_macro)
            
            m_steps = micro_dict.get(m_title, [])
            # Rule: Fast-track skips the second/harder concepts inside macros
            if rt["type"] == "fast_track" and len(m_steps) > 1:
                m_steps = [m_steps[0]] 
            
            for m_step in m_steps:
                new_micro = models.MicroStep(
                    macro_step_id=new_macro.id,
                    title=m_step[0],
                    description=m_step[1],
                    difficulty=m_step[2],
                    weight=m_step[3],
                    resource_link=RESOURCE_LINKS.get(m_step[0], "#")
                )
                db.add(new_micro)
                db.commit()
                db.refresh(new_micro)
                create_quiz_for_micro_step(db, new_micro.id, new_micro.title)

def create_quiz_for_micro_step(db, micro_step_id: int, topic_name: str):
    # Check if a quiz already exists for this micro step
    existing_quiz = db.query(models.Quiz).filter(models.Quiz.micro_step_id == micro_step_id).first()
    if existing_quiz:
        return
        
    new_quiz = models.Quiz(micro_step_id=micro_step_id, topic_name=topic_name)
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    
    from quiz_pool import QUIZ_POOL
    pool_questions = QUIZ_POOL.get(topic_name, [])
    for pq in pool_questions:
        q = models.QuizQuestion(
            quiz_id=new_quiz.id,
            question_text=pq["question_text"],
            option_a=pq["option_a"],
            option_b=pq["option_b"],
            option_c=pq["option_c"],
            option_d=pq["option_d"],
            correct_answer=pq["correct_answer"]
        )
        db.add(q)
    db.commit()


