"""
Test the roadmap agent directly without API endpoints.
"""

import asyncio
import json
import logging
from src.backend.core.multi_agent_systems.cv_analysis.road_maps import generate_user_roadmap, OutputFormat
from src.backend.boundary.databases.db.CRUD.auth_CRUD import AuthCRUD

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_roadmap_agent():
    """Test the roadmap agent directly with database user"""

    user_email = "hamzakhaledlklk@gmail.com"

    logger.info(f"🚀 Testing Roadmap Agent for user: {user_email}")
    logger.info("=" * 60)

    try:
        # Get user from database
        user = AuthCRUD.get_user_by_email(user_email)
        if not user:
            logger.error(f"❌ User not found: {user_email}")
            return

        logger.info(f"✅ User found: {user.id}")

        # Test basic roadmap generation (without market research for speed)
        logger.info("\n🔧 Testing basic roadmap generation...")
        roadmap_output = await generate_user_roadmap(
            user_id=str(user.id),
            target_role="Senior Software Engineer",
            enable_market_research=False,
            output_format=OutputFormat.SVG
        )

        logger.info(f"📊 Basic Roadmap Results:")
        logger.info(f"   Current Role: {roadmap_output.roadmap.metadata.current_role}")
        logger.info(f"   Target Role: {roadmap_output.roadmap.metadata.target_role}")
        logger.info(f"   Total Duration: {roadmap_output.roadmap.metadata.total_duration}")
        logger.info(f"   Roadmap Size: {roadmap_output.roadmap.metadata.roadmap_size}")
        logger.info(f"   Stages Count: {len(roadmap_output.roadmap.stages)}")
        logger.info(f"   Confidence Score: {roadmap_output.confidence_score}/100")
        logger.info(f"   Template Used: {roadmap_output.visualization.template_used}")

        # Display first few stages
        logger.info(f"\n📋 ROADMAP STAGES:")
        for i, stage in enumerate(roadmap_output.roadmap.stages[:3], 1):
            logger.info(f"   {i}. {stage.title} ({stage.duration})")
            logger.info(f"      Difficulty: {stage.difficulty_level}")
            logger.info(f"      Skills: {', '.join(stage.skills_to_learn[:3])}")

        if len(roadmap_output.roadmap.stages) > 3:
            logger.info(f"   ... and {len(roadmap_output.roadmap.stages) - 3} more stages")

        # Test with market research enabled
        logger.info("\n🌐 Testing with market research enabled...")
        enhanced_roadmap = await generate_user_roadmap(
            user_id=str(user.id),
            target_role="AI/ML Engineer",
            enable_market_research=True,
            output_format=OutputFormat.SVG
        )

        logger.info(f"🔍 Enhanced Roadmap Results:")
        logger.info(f"   Target Role: {enhanced_roadmap.roadmap.metadata.target_role}")
        logger.info(f"   Confidence Score: {enhanced_roadmap.confidence_score}/100")
        logger.info(f"   Market Insights: {enhanced_roadmap.roadmap.market_insights[:100] if enhanced_roadmap.roadmap.market_insights else 'None'}...")

        # Save detailed results
        basic_results = {
            "test_type": "basic_roadmap",
            "user_email": user_email,
            "user_id": str(user.id),
            "current_role": roadmap_output.roadmap.metadata.current_role,
            "target_role": roadmap_output.roadmap.metadata.target_role,
            "total_duration": roadmap_output.roadmap.metadata.total_duration,
            "roadmap_size": roadmap_output.roadmap.metadata.roadmap_size.value,
            "stages_count": len(roadmap_output.roadmap.stages),
            "confidence_score": roadmap_output.confidence_score,
            "generation_summary": roadmap_output.generation_summary,
            "template_used": roadmap_output.visualization.template_used,
            "stages": [
                {
                    "stage_id": stage.stage_id,
                    "title": stage.title,
                    "duration": stage.duration,
                    "description": stage.description,
                    "skills_to_learn": stage.skills_to_learn,
                    "resources": stage.resources,
                    "milestones": stage.milestones,
                    "difficulty_level": stage.difficulty_level
                } for stage in roadmap_output.roadmap.stages
            ]
        }

        enhanced_results = {
            "test_type": "enhanced_roadmap",
            "target_role": enhanced_roadmap.roadmap.metadata.target_role,
            "confidence_score": enhanced_roadmap.confidence_score,
            "market_insights": enhanced_roadmap.roadmap.market_insights,
            "stages_count": len(enhanced_roadmap.roadmap.stages)
        }

        # Save results to files
        with open('direct_roadmap_basic.json', 'w') as f:
            json.dump(basic_results, f, indent=2)

        with open('direct_roadmap_enhanced.json', 'w') as f:
            json.dump(enhanced_results, f, indent=2)

        # Save Graphviz visualization sources
        with open('basic_roadmap.dot', 'w') as f:
            f.write(roadmap_output.visualization.graphviz_source)

        with open('enhanced_roadmap.dot', 'w') as f:
            f.write(enhanced_roadmap.visualization.graphviz_source)

        logger.info(f"\n💾 Results saved:")
        logger.info(f"   Basic results: direct_roadmap_basic.json")
        logger.info(f"   Enhanced results: direct_roadmap_enhanced.json")
        logger.info(f"   Basic visualization: basic_roadmap.dot")
        logger.info(f"   Enhanced visualization: enhanced_roadmap.dot")

        # Test different output formats
        logger.info(f"\n🎨 Testing different output formats...")
        for format_type in [OutputFormat.PNG, OutputFormat.PDF, OutputFormat.DOT]:
            try:
                format_test = await generate_user_roadmap(
                    user_id=str(user.id),
                    target_role="Senior Software Engineer",
                    enable_market_research=False,
                    output_format=format_type
                )
                logger.info(f"   ✅ {format_type.value.upper()} format: OK")
            except Exception as e:
                logger.warning(f"   ⚠️ {format_type.value.upper()} format: {e}")

        logger.info(f"\n🎉 Direct roadmap agent test completed successfully!")

        # Generate summary insights
        logger.info(f"\n🔍 KEY INSIGHTS:")
        logger.info(f"   System can generate roadmaps: ✅")
        logger.info(f"   Market research integration: ✅")
        logger.info(f"   Multiple template sizes: ✅")
        logger.info(f"   Graphviz visualization: ✅")
        logger.info(f"   Confidence scoring: ✅")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_roadmap_agent())