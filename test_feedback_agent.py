"""
Test the feedback agent with mock user hamzakhaledlklk@gmail.com
"""

import asyncio
import json
import logging
from src.backend.core.multi_agent_systems.cv_analysis.feedback import analyze_user_resume
from src.backend.boundary.databases.db.CRUD.auth_CRUD import AuthCRUD

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_feedback_agent():
    """Test the feedback agent with the specified mock user"""

    user_email = "hamzakhaledlklk@gmail.com"

    logger.info(f"🚀 Testing Feedback Agent for user: {user_email}")
    logger.info("=" * 60)

    try:
        # Get user from database
        user = AuthCRUD.get_user_by_email(user_email)
        if not user:
            logger.error(f"❌ User not found: {user_email}")
            return

        logger.info(f"✅ User found: {user.id}")

        # Test without market research first
        logger.info("\n📊 Testing feedback WITHOUT market research...")
        feedback_basic = await analyze_user_resume(
            user_id=str(user.id),  # Convert UUID to string
            enable_market_research=False
        )

        logger.info(f"📈 Basic Analysis Results:")
        logger.info(f"   Overall Score: {feedback_basic.overall_score}/100")
        logger.info(f"   Summary: {feedback_basic.summary}")
        logger.info(f"   Skills Analyzed: {len(feedback_basic.skills_analysis)}")
        logger.info(f"   Section Feedback: {len(feedback_basic.section_feedback)}")
        logger.info(f"   Top Recommendations: {len(feedback_basic.top_recommendations)}")

        # Test with market research
        logger.info("\n🌐 Testing feedback WITH market research...")
        feedback_market = await analyze_user_resume(
            user_id=str(user.id),  # Convert UUID to string
            enable_market_research=True
        )

        logger.info(f"📈 Market-Enhanced Analysis Results:")
        logger.info(f"   Overall Score: {feedback_market.overall_score}/100")
        logger.info(f"   Summary: {feedback_market.summary}")
        logger.info(f"   Skills Analyzed: {len(feedback_market.skills_analysis)}")
        logger.info(f"   Market Alignment: {feedback_market.market_alignment or 'N/A'}")
        logger.info(f"   Top Recommendations: {len(feedback_market.top_recommendations)}")

        # Save detailed results
        results = {
            "user_email": user_email,
            "user_id": str(user.id),
            "basic_feedback": {
                "overall_score": feedback_basic.overall_score,
                "summary": feedback_basic.summary,
                "skills_analysis": [
                    {
                        "skill_name": skill.skill_name,
                        "current_level": skill.current_level,
                        "market_demand": skill.market_demand,
                        "improvement_suggestions": skill.improvement_suggestions
                    } for skill in feedback_basic.skills_analysis
                ],
                "section_feedback": [
                    {
                        "section_name": section.section_name,
                        "strengths": section.strengths,
                        "weaknesses": section.weaknesses,
                        "suggestions": section.suggestions
                    } for section in feedback_basic.section_feedback
                ],
                "top_recommendations": feedback_basic.top_recommendations
            },
            "market_enhanced_feedback": {
                "overall_score": feedback_market.overall_score,
                "summary": feedback_market.summary,
                "market_alignment": feedback_market.market_alignment,
                "skills_analysis": [
                    {
                        "skill_name": skill.skill_name,
                        "current_level": skill.current_level,
                        "market_demand": skill.market_demand,
                        "improvement_suggestions": skill.improvement_suggestions
                    } for skill in feedback_market.skills_analysis
                ],
                "top_recommendations": feedback_market.top_recommendations
            }
        }

        with open('feedback_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)

        logger.info(f"\n💾 Detailed results saved to: feedback_test_results.json")

        # Display some key insights
        logger.info(f"\n🎯 KEY INSIGHTS:")
        logger.info(f"   Basic vs Market Score: {feedback_basic.overall_score} → {feedback_market.overall_score}")

        if feedback_basic.skills_analysis:
            logger.info(f"\n📋 SKILLS ANALYZED:")
            for skill in feedback_basic.skills_analysis[:3]:  # Show first 3
                logger.info(f"   • {skill.skill_name}: {skill.current_level}")

        if feedback_basic.top_recommendations:
            logger.info(f"\n🔝 TOP RECOMMENDATIONS:")
            for i, rec in enumerate(feedback_basic.top_recommendations[:3], 1):
                logger.info(f"   {i}. {rec}")

        logger.info(f"\n✅ Feedback agent test completed successfully!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_feedback_agent())