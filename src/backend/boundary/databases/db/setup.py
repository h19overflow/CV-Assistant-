"""
Database setup and testing script.
Creates all tables and tests basic operations.
"""
from src.backend.boundary.databases.db import AuthCRUD
from .engine import get_db_manager, get_session_context
from .models import User, Resume, Section, Feedback


def create_all_tables():
    """Create all database tables"""
    print("🔨 Creating database tables...")

    db_manager = get_db_manager()
    try:
        db_manager.create_tables()
        print("✅ All tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def test_database_operations():
    """Test basic database operations"""
    print("🧪 Testing database operations...")

    try:
        with get_session_context() as session:
            # Test 1: Create a user
            test_user = AuthCRUD.create_user(
                email="hamzakhaledlklk@gmail.com",
                password='testpassword')

            # Test 2: Create a resume
            test_resume = Resume(
                user_id=test_user.id,
                original_text="This is a test resume content...",
                filename="test_resume.pdf",
                summary="Test summary"
            )
            session.add(test_resume)
            session.commit()
            print(f"✅ Created resume: {test_resume}")

            # Test 3: Create a section
            test_section = Section(
                resume_id=test_resume.id,
                section_type="Experience",
                content="Software Engineer at Test Company",
                start_pos=0,
                end_pos=35
            )
            session.add(test_section)
            session.commit()
            print(f"✅ Created section: {test_section}")


            # Test 5: Create feedback
            test_feedback = Feedback(
                resume_id=test_resume.id,
                feedback_text="Great resume! Consider adding more technical details.",
                category="Technical Skills"
            )
            session.add(test_feedback)
            session.commit()
            print(f"✅ Created feedback: {test_feedback}")

            # Test 6: Query relationships
            user_with_resumes = session.query(User).filter(User.email == "hamzakhaledlklk@gmail.com").first()
            print(f"✅ User has {len(user_with_resumes.resumes)} resume(s)")

            resume_with_sections = user_with_resumes.resumes[0]
            print(f"✅ Resume has {len(resume_with_sections.sections)} section(s)")
            print(f"✅ Resume has {len(resume_with_sections.feedback)} feedback item(s)")

            section_with_entities = resume_with_sections.sections[0]
            print(f"✅ Section has {len(section_with_entities.entities)} entity/entities")

            # Cleanup test data
            session.delete(test_user)  # Cascades to all related records
            session.commit()
            print("🧹 Cleaned up test data")

        print("✅ All database tests passed!")
        return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def setup_and_test():
    """Complete database setup and testing"""
    with get_session_context() as session:
        result = session.query(User).first()
        print(AuthCRUD.verify_password(password='testpassword', hashed=result.password_hash))
    return True


if __name__ == "__main__":
    setup_and_test()