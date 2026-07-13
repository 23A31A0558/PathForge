# backend/verify_multi_roadmap.py
import os
import sys
import unittest
from unittest.mock import patch

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
import schemas
import database
from main import app

# Create test engine and session
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def mock_generate_personalized_roadmap(profile_data):
    career = profile_data["career"]
    return {
        "roadmaps": [
            {
                "title": f"{career} - Fast Track",
                "description": f"Fast track roadmap for {career}",
                "phases": [
                    {
                        "phase_number": 1,
                        "phase_title": "Fundamentals of " + career,
                        "estimated_duration": "2 weeks",
                        "topics": [
                            {
                                "topic": "Introduction to " + career,
                                "difficulty": "easy",
                                "estimated_hours": 2,
                                "resources": [{"title": "Docs", "url": "http://example.com"}],
                                "mini_project": "Simple CLI app",
                                "quiz_required": True
                            }
                        ]
                    }
                ]
            },
            {
                "title": f"{career} - Deep Learning",
                "description": f"Deep learning roadmap for {career}",
                "phases": [
                    {
                        "phase_number": 1,
                        "phase_title": "Advanced Topics in " + career,
                        "estimated_duration": "4 weeks",
                        "topics": [
                            {
                                "topic": "Deep Dive into " + career,
                                "difficulty": "hard",
                                "estimated_hours": 10,
                                "resources": [{"title": "Advanced Book", "url": "http://example.com/adv"}],
                                "mini_project": "Enterprise service",
                                "quiz_required": True
                            }
                        ]
                    }
                ]
            }
        ]
    }

class TestMultiRoadmap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = TestingSessionLocal()
        
        # Clean up database test users and their data if they exist
        cls.cleanup_test_data()

        # Register User 1
        resp = cls.client.post("/register", json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "Password123!"
        })
        assert resp.status_code == 200, resp.text
        
        # Log in User 1
        resp = cls.client.post("/login", data={"username": "user1", "password": "Password123!"})
        assert resp.status_code == 200
        cls.token1 = resp.json()["access_token"]
        cls.headers1 = {"Authorization": f"Bearer {cls.token1}"}

        # Register User 2 (Attacker)
        resp = cls.client.post("/register", json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "Password123!"
        })
        assert resp.status_code == 200
        
        # Log in User 2
        resp = cls.client.post("/login", data={"username": "user2", "password": "Password123!"})
        assert resp.status_code == 200
        cls.token2 = resp.json()["access_token"]
        cls.headers2 = {"Authorization": f"Bearer {cls.token2}"}

    @classmethod
    def cleanup_test_data(cls):
        # Find user IDs matching usernames
        user_ids = {u.id for u in cls.db.query(models.User).filter(models.User.username.in_(["user1", "user2"])).all()}
        # Include a range of IDs that might be generated in test runs to clean up orphaned records
        user_ids.update([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
        user_ids_list = list(user_ids)
        
        cls.db.query(models.RoadmapQuestionnaire).filter(models.RoadmapQuestionnaire.user_id.in_(user_ids_list)).delete(synchronize_session=False)
        cls.db.query(models.Answer).filter(models.Answer.user_id.in_(user_ids_list)).delete(synchronize_session=False)
        cls.db.query(models.Progress).filter(models.Progress.user_id.in_(user_ids_list)).delete(synchronize_session=False)
        cls.db.query(models.QuizAttempt).filter(models.QuizAttempt.user_id.in_(user_ids_list)).delete(synchronize_session=False)
        cls.db.query(models.RoadmapGenerationStatus).filter(models.RoadmapGenerationStatus.user_id.in_(user_ids_list)).delete(synchronize_session=False)
        
        roadmaps = cls.db.query(models.Roadmap).filter(models.Roadmap.user_id.in_(user_ids_list)).all()
        roadmap_ids = [r.id for r in roadmaps]
        if roadmap_ids:
            phases = cls.db.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id.in_(roadmap_ids)).all()
            phase_ids = [p.id for p in phases]
            if phase_ids:
                cls.db.query(models.RoadmapTopic).filter(models.RoadmapTopic.phase_id.in_(phase_ids)).delete(synchronize_session=False)
            cls.db.query(models.RoadmapPhase).filter(models.RoadmapPhase.roadmap_id.in_(roadmap_ids)).delete(synchronize_session=False)
            cls.db.query(models.Roadmap).filter(models.Roadmap.user_id.in_(user_ids_list)).delete(synchronize_session=False)
        
        cls.db.query(models.User).filter(models.User.username.in_(["user1", "user2"])).delete(synchronize_session=False)
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.cleanup_test_data()
        cls.db.close()

    @patch('roadmap_ai_service.generate_personalized_roadmap', side_effect=mock_generate_personalized_roadmap)
    @patch('groq_ai_service.generate_personalized_roadmap', side_effect=mock_generate_personalized_roadmap)
    @patch.dict('os.environ', {'GROQ_API_KEY': 'mock_groq_key'})
    def test_multi_roadmap_flow(self, mock_main_groq, mock_service_groq):
        print("\n--- Running Multi-Roadmap Verification Flow ---")

        # 1. Submit questionnaire for Backend Development
        resp = self.client.post("/questionnaire", headers=self.headers1, json={
            "name": "User One",
            "college": "Test College",
            "year": "3",
            "branch": "Computer Science",
            "programming_languages": ["Python", "Go"],
            "primary_career_goal": "Backend Development",
            "current_skill_level": "Intermediate",
            "daily_learning_time": "2 hours",
            "target_timeline": "6 months"
        })
        self.assertEqual(resp.status_code, 200)
        print("[OK] Backend Development questionnaire submitted.")

        # 2. Check generated roadmaps
        resp = self.client.get("/roadmaps/list", headers=self.headers1)
        self.assertEqual(resp.status_code, 200)
        list1 = resp.json()
        self.assertEqual(len(list1), 2)  # Fast track & Deep learning
        backend_ft_id = [r["id"] for r in list1 if "Backend Development - Fast Track" in r["title"]][0]
        backend_dl_id = [r["id"] for r in list1 if "Backend Development - Deep Learning" in r["title"]][0]
        print(f"[OK] Backend roadmaps generated. Fast Track ID: {backend_ft_id}, Deep Learning ID: {backend_dl_id}")

        # 3. Submit questionnaire for Frontend Development
        resp = self.client.post("/questionnaire", headers=self.headers1, json={
            "name": "User One",
            "college": "Test College",
            "year": "3",
            "branch": "Computer Science",
            "programming_languages": ["JavaScript", "HTML"],
            "primary_career_goal": "Frontend Development",
            "current_skill_level": "Intermediate",
            "daily_learning_time": "2 hours",
            "target_timeline": "6 months"
        })
        self.assertEqual(resp.status_code, 200)
        print("[OK] Frontend Development questionnaire submitted.")

        # Check total roadmaps list
        resp = self.client.get("/roadmaps/list", headers=self.headers1)
        list2 = resp.json()
        self.assertEqual(len(list2), 4) # 2 backend + 2 frontend
        frontend_ft_id = [r["id"] for r in list2 if "Frontend Development - Fast Track" in r["title"]][0]
        frontend_dl_id = [r["id"] for r in list2 if "Frontend Development - Deep Learning" in r["title"]][0]
        print(f"[OK] Frontend roadmaps generated. Fast Track ID: {frontend_ft_id}, Deep Learning ID: {frontend_dl_id}")

        # 4. Submit questionnaire for AI Engineer
        resp = self.client.post("/questionnaire", headers=self.headers1, json={
            "name": "User One",
            "college": "Test College",
            "year": "3",
            "branch": "Computer Science",
            "programming_languages": ["Python", "R"],
            "primary_career_goal": "AI Engineer",
            "current_skill_level": "Intermediate",
            "daily_learning_time": "2 hours",
            "target_timeline": "6 months"
        })
        self.assertEqual(resp.status_code, 200)
        print("[OK] AI Engineer questionnaire submitted.")

        # Check total roadmaps list (Verify all three exist)
        resp = self.client.get("/roadmaps/list", headers=self.headers1)
        list3 = resp.json()
        self.assertEqual(len(list3), 6) # 2 backend + 2 frontend + 2 AI
        ai_ft_id = [r["id"] for r in list3 if "AI Engineer - Fast Track" in r["title"]][0]
        ai_dl_id = [r["id"] for r in list3 if "AI Engineer - Deep Learning" in r["title"]][0]
        print(f"[OK] AI Engineer roadmaps generated. Fast Track ID: {ai_ft_id}, Deep Learning ID: {ai_dl_id}")

        # 5. Check active selected roadmap status
        resp = self.client.get("/users/me", headers=self.headers1)
        user_info = resp.json()
        selected_id = user_info["selected_roadmap_id"]
        # AI Engineer should be currently selected since it was the last generated
        self.assertIn(selected_id, [ai_ft_id, ai_dl_id])
        print(f"[OK] Currently active selected roadmap ID: {selected_id}")

        # 6. Verify progress isolation: Complete a topic in Frontend Development
        # Load Frontend Deep Learning roadmap details to get the RoadmapTopic ID
        resp = self.client.get(f"/roadmap/{frontend_dl_id}", headers=self.headers1)
        self.assertEqual(resp.status_code, 200)
        fd_roadmap = resp.json()
        topic_id = fd_roadmap["macro_steps"][0]["micro_steps"][0]["id"]
        
        # Complete Frontend topic
        resp = self.client.post("/progress/complete", headers=self.headers1, json={"micro_step_id": topic_id})
        self.assertEqual(resp.status_code, 200)
        print(f"[OK] Completed Frontend Deep Learning topic: {topic_id}")

        # Check frontend progress
        resp = self.client.get("/roadmaps/list", headers=self.headers1)
        list_after_complete = resp.json()
        
        fd_prog = [r["progress"] for r in list_after_complete if r["id"] == frontend_dl_id][0]
        be_prog = [r["progress"] for r in list_after_complete if r["id"] == backend_dl_id][0]
        ai_prog = [r["progress"] for r in list_after_complete if r["id"] == ai_dl_id][0]
        
        self.assertGreater(fd_prog, 0.0)
        self.assertEqual(be_prog, 0.0)
        self.assertEqual(ai_prog, 0.0)
        print(f"[OK] Progress Isolation verified: Frontend DL progress={fd_prog}%, Backend DL progress={be_prog}%, AI DL progress={ai_prog}%")

        # 7. Verify Notes Isolation
        # Notes are saved in client localStorage using unique topic ID, so we verify topic IDs are different
        be_roadmap = self.client.get(f"/roadmap/{backend_dl_id}", headers=self.headers1).json()
        be_topic_id = be_roadmap["macro_steps"][0]["micro_steps"][0]["id"]
        self.assertNotEqual(topic_id, be_topic_id)
        print(f"[OK] Notes Isolation verified (Different database topic IDs: Frontend={topic_id}, Backend={be_topic_id})")

        # Fetch the quiz first to initialize/create it
        resp = self.client.get(f"/quiz/{topic_id}", headers=self.headers1)
        self.assertEqual(resp.status_code, 200)

        # Take a quiz for the Frontend topic
        resp = self.client.post("/quiz/submit", headers=self.headers1, json={
            "micro_step_id": topic_id,
            "answers": []
        })
        self.assertEqual(resp.status_code, 200)
        print("[OK] Submitted quiz for Frontend topic.")
        
        # Check backend quiz attempts (should be 0 for backend topic)
        db_attempts_be = self.db.query(models.QuizAttempt).filter(
            models.QuizAttempt.user_id == user_info["id"],
            models.QuizAttempt.micro_step_id == be_topic_id
        ).count()
        self.assertEqual(db_attempts_be, 0)
        print(f"[OK] Quiz Attempts Isolation verified: quiz attempts for Backend topic = {db_attempts_be}")

        # 9. Verify 403 Forbidden ownership checks for User 2 (Attacker)
        # Attempt to access User 1's Backend roadmap
        resp = self.client.get(f"/roadmap/{backend_dl_id}", headers=self.headers2)
        self.assertEqual(resp.status_code, 403)
        print("[OK] Accessing non-owned roadmap returned 403 Forbidden.")
        
        # Attempt to select User 1's Backend roadmap
        resp = self.client.post(f"/roadmap/select/{backend_dl_id}", headers=self.headers2)
        self.assertEqual(resp.status_code, 403)
        print("[OK] Selecting non-owned roadmap returned 403 Forbidden.")

        # Attempt to rename User 1's Backend roadmap
        resp = self.client.put(f"/roadmap/rename/{backend_dl_id}", headers=self.headers2, json={"title": "Hacked Title"})
        self.assertEqual(resp.status_code, 403)
        print("[OK] Renaming non-owned roadmap returned 403 Forbidden.")

        # Attempt to archive User 1's Backend roadmap
        resp = self.client.post(f"/roadmap/archive/{backend_dl_id}", headers=self.headers2)
        self.assertEqual(resp.status_code, 403)
        print("[OK] Archiving non-owned roadmap returned 403 Forbidden.")

        # Attempt to delete User 1's Backend roadmap
        resp = self.client.delete(f"/roadmap/delete/{backend_dl_id}", headers=self.headers2)
        self.assertEqual(resp.status_code, 403)
        print("[OK] Deleting non-owned roadmap returned 403 Forbidden.")

        # 10. Rename Frontend roadmap (User 1)
        resp = self.client.put(f"/roadmap/rename/{frontend_dl_id}", headers=self.headers1, json={"title": "Modern Frontend Path"})
        self.assertEqual(resp.status_code, 200)
        # Check list for renamed title
        resp = self.client.get("/roadmaps/list", headers=self.headers1)
        title = [r["title"] for r in resp.json() if r["id"] == frontend_dl_id][0]
        self.assertEqual(title, "Modern Frontend Path")
        print(f"[OK] Renamed Frontend roadmap. New title: '{title}'")

        # 11. Archive AI roadmap (User 1)
        resp = self.client.post(f"/roadmap/archive/{ai_dl_id}", headers=self.headers1)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()["is_archived"])
        print("[OK] Archived AI Deep Learning roadmap.")

        # 12. Delete Backend roadmap (User 1)
        resp = self.client.delete(f"/roadmap/delete/{backend_dl_id}", headers=self.headers1)
        self.assertEqual(resp.status_code, 200)
        print("[OK] Deleted Backend Deep Learning roadmap.")
        
        # Check lists (should contain only 5 roadmaps now)
        resp = self.client.get("/roadmaps/list", headers=self.headers1)
        self.assertEqual(len(resp.json()), 5)
        print("[OK] Remaining roadmaps list length is 5. Backend Deep Learning roadmap successfully deleted.")

        # 13. Regenerate Frontend roadmap
        resp = self.client.post(f"/roadmap/regenerate/{frontend_dl_id}", headers=self.headers1)
        self.assertEqual(resp.status_code, 200)
        new_roadmap_id = resp.json()["new_roadmap_id"]
        print(f"[OK] Regenerated Frontend roadmap. New Roadmap ID: {new_roadmap_id}")
        
        # Verify old roadmap is deleted
        old_rm = self.db.query(models.Roadmap).filter(models.Roadmap.id == frontend_dl_id).first()
        self.assertIsNone(old_rm)
        print("[OK] Confirmed old Frontend roadmap has been deleted.")

        print("--- All Multi-Roadmap Verification Tests Passed! ---")

if __name__ == "__main__":
    unittest.main()
