"""
Test the complete roadmap generation system including multi-agent pipeline and API endpoints.
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from src.backend.core.multi_agent_systems.cv_analysis.road_maps import generate_user_roadmap, OutputFormat

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RoadmapSystemTester:
    """Comprehensive test suite for roadmap generation system"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.access_token = None
        self.user_data = {
            "email": "hamzakhaledlklk@gmail.com",
            "password": "SecurePassword123!"
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def register_and_login(self) -> bool:
        """Register and login to get access token"""
        logger.info("🔧 Setting up authentication...")

        # Register (might already exist)
        register_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }

        async with self.session.post(f"{self.base_url}/auth/register", json=register_data) as response:
            if response.status == 201:
                logger.info("✅ User registered successfully")
            elif response.status == 400:
                logger.info("ℹ️ User already exists, proceeding to login")

        # Login
        login_data = aiohttp.FormData()
        login_data.add_field('username', self.user_data["email"])
        login_data.add_field('password', self.user_data["password"])

        async with self.session.post(f"{self.base_url}/auth/login", data=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.access_token = data.get("access_token")
                logger.info(f"✅ Login successful! Token: {self.access_token[:20]}...")
                return True
            else:
                error = await response.text()
                logger.error(f"❌ Login failed: {error}")
                return False

    async def test_direct_agent(self) -> bool:
        """Test the roadmap agent directly (without API)"""
        logger.info("\n🤖 Testing direct roadmap agent...")

        try:
            # Test with mock user from database
            from src.backend.boundary.databases.db.CRUD.auth_CRUD import AuthCRUD

            user = AuthCRUD.get_user_by_email(self.user_data["email"])
            if not user:
                logger.error("❌ User not found in database")
                return False

            # Generate roadmap without market research first (faster)
            roadmap_output = await generate_user_roadmap(
                user_id=str(user.id),
                target_role="Senior Software Engineer",
                enable_market_research=False,
                output_format=OutputFormat.SVG
            )

            logger.info(f"✅ Direct agent test completed!")
            logger.info(f"   Current Role: {roadmap_output.roadmap.metadata.current_role}")
            logger.info(f"   Target Role: {roadmap_output.roadmap.metadata.target_role}")
            logger.info(f"   Duration: {roadmap_output.roadmap.metadata.total_duration}")
            logger.info(f"   Stages: {len(roadmap_output.roadmap.stages)}")
            logger.info(f"   Confidence Score: {roadmap_output.confidence_score}/100")
            logger.info(f"   Size Category: {roadmap_output.roadmap.metadata.roadmap_size}")

            # Save detailed results
            direct_results = {
                "current_role": roadmap_output.roadmap.metadata.current_role,
                "target_role": roadmap_output.roadmap.metadata.target_role,
                "total_duration": roadmap_output.roadmap.metadata.total_duration,
                "roadmap_size": roadmap_output.roadmap.metadata.roadmap_size.value,
                "stages_count": len(roadmap_output.roadmap.stages),
                "confidence_score": roadmap_output.confidence_score,
                "generation_summary": roadmap_output.generation_summary,
                "stages": [
                    {
                        "title": stage.title,
                        "duration": stage.duration,
                        "description": stage.description,
                        "skills_to_learn": stage.skills_to_learn,
                        "difficulty_level": stage.difficulty_level
                    } for stage in roadmap_output.roadmap.stages
                ],
                "graphviz_source_length": len(roadmap_output.visualization.graphviz_source),
                "template_used": roadmap_output.visualization.template_used
            }

            with open('direct_roadmap_results.json', 'w') as f:
                json.dump(direct_results, f, indent=2)

            # Save Graphviz source for inspection
            with open('roadmap_visualization.dot', 'w') as f:
                f.write(roadmap_output.visualization.graphviz_source)

            logger.info("💾 Direct agent results saved to: direct_roadmap_results.json")
            logger.info("📊 Graphviz source saved to: roadmap_visualization.dot")

            return True

        except Exception as e:
            logger.error(f"❌ Direct agent test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_roadmap_api_endpoint(self) -> bool:
        """Test the roadmap API endpoint"""
        logger.info("\n🌐 Testing roadmap API endpoint...")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        request_data = {
            "target_role": "Senior Machine Learning Engineer",
            "enable_market_research": False,  # Faster for testing
            "output_format": "svg",
            "max_stages": 6
        }

        async with self.session.post(
            f"{self.base_url}/ai/roadmap/generate",
            json=request_data,
            headers=headers
        ) as response:
            logger.info(f"API Response status: {response.status}")

            if response.status == 200:
                data = await response.json()
                logger.info(f"✅ API roadmap generated!")
                logger.info(f"   Current Role: {data['current_role']}")
                logger.info(f"   Target Role: {data['target_role']}")
                logger.info(f"   Duration: {data['total_duration']}")
                logger.info(f"   Stages Count: {data['stages_count']}")
                logger.info(f"   Confidence Score: {data['confidence_score']}/100")
                logger.info(f"   Size Category: {data['roadmap_size']}")
                logger.info(f"   Visualization Format: {data['visualization_format']}")

                # Save API results
                with open('api_roadmap_results.json', 'w') as f:
                    json.dump(data, f, indent=2)

                logger.info("💾 API results saved to: api_roadmap_results.json")
                return True

            else:
                error = await response.text()
                logger.error(f"❌ API endpoint failed: {error}")
                return False

    async def test_market_research_enabled(self) -> bool:
        """Test roadmap generation with market research enabled"""
        logger.info("\n🔍 Testing with market research enabled...")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        request_data = {
            "target_role": "AI/ML Engineer",
            "enable_market_research": True,
            "output_format": "svg",
            "max_stages": 5
        }

        async with self.session.post(
            f"{self.base_url}/ai/roadmap/generate",
            json=request_data,
            headers=headers
        ) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"✅ Market research roadmap generated!")
                logger.info(f"   Target Role: {data['target_role']}")
                logger.info(f"   Confidence Score: {data['confidence_score']}/100")
                logger.info(f"   Market Research: {data['market_research_included']}")

                # Save market research results
                with open('market_research_roadmap.json', 'w') as f:
                    json.dump(data, f, indent=2)

                return True
            else:
                error = await response.text()
                logger.error(f"❌ Market research test failed: {error}")
                return False

    async def test_formats_endpoint(self) -> bool:
        """Test the supported formats endpoint"""
        logger.info("\n📋 Testing formats endpoint...")

        async with self.session.get(f"{self.base_url}/ai/roadmap/formats") as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"✅ Formats endpoint working!")
                logger.info(f"   Supported formats: {len(data['formats'])}")
                logger.info(f"   Recommended: {data['recommended']}")

                for fmt in data['formats']:
                    logger.info(f"   • {fmt['format']}: {fmt['description']}")

                return True
            else:
                logger.error(f"❌ Formats endpoint failed")
                return False

    async def test_unauthorized_access(self) -> bool:
        """Test that roadmap endpoints require authentication"""
        logger.info("\n🚫 Testing unauthorized access...")

        request_data = {"target_role": "Senior Developer"}

        async with self.session.post(
            f"{self.base_url}/ai/roadmap/generate",
            json=request_data
            # No Authorization header
        ) as response:
            if response.status == 401:
                logger.info("✅ Correctly rejected unauthorized request")
                return True
            else:
                logger.error(f"❌ Should have rejected unauthorized request, got {response.status}")
                return False

    async def run_complete_test_suite(self):
        """Run complete roadmap system test suite"""
        logger.info(f"\n🎯 ROADMAP SYSTEM COMPREHENSIVE TEST")
        logger.info(f"Target: {self.base_url}")
        logger.info(f"Time: {datetime.now().isoformat()}")
        logger.info("=" * 70)

        # Track test results
        test_results = {}

        # Test unauthorized access first
        test_results["unauthorized_rejection"] = await self.test_unauthorized_access()

        # Login
        login_success = await self.register_and_login()
        test_results["authentication"] = login_success

        if not login_success:
            logger.error("❌ Cannot proceed without authentication")
            return

        # Test direct agent
        test_results["direct_agent"] = await self.test_direct_agent()

        # Test API endpoints
        test_results["basic_api"] = await self.test_roadmap_api_endpoint()
        test_results["market_research"] = await self.test_market_research_enabled()
        test_results["formats_endpoint"] = await self.test_formats_endpoint()

        # Generate test summary
        logger.info(f"\n📊 COMPREHENSIVE TEST SUMMARY:")
        logger.info("=" * 50)

        total_tests = len(test_results)
        passed_tests = sum(test_results.values())

        for test_name, passed in test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"   {test_name:20s}: {status}")

        logger.info(f"\n🎯 OVERALL RESULT:")
        logger.info(f"   Tests Passed: {passed_tests}/{total_tests}")
        logger.info(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if passed_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED! Roadmap system is fully functional.")
        elif passed_tests >= total_tests * 0.8:
            logger.info("⚠️ Most tests passed. System is mostly functional with minor issues.")
        else:
            logger.warning("🚨 Multiple test failures. System needs attention.")

        # Save test summary
        summary = {
            "test_timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "test_results": test_results
        }

        with open('roadmap_test_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"💾 Test summary saved to: roadmap_test_summary.json")

async def main():
    """Main test execution"""
    async with RoadmapSystemTester() as tester:
        await tester.run_complete_test_suite()

if __name__ == "__main__":
    asyncio.run(main())