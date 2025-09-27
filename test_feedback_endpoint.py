"""
Test the AI feedback endpoints with authentication
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeedbackEndpointTester:
    """Test the AI feedback endpoints"""

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
        """Register user if needed, then login"""
        # Try to register first (might already exist)
        logger.info("🔧 Registering user (if needed)...")

        register_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }

        async with self.session.post(
            f"{self.base_url}/auth/register",
            json=register_data
        ) as response:
            if response.status == 201:
                logger.info("✅ User registered successfully")
            elif response.status == 400:
                logger.info("ℹ️ User already exists, proceeding to login")
            else:
                error = await response.text()
                logger.warning(f"⚠️ Registration issue: {error}")

        # Now login
        logger.info("🔑 Logging in to get access token...")

        login_data = aiohttp.FormData()
        login_data.add_field('username', self.user_data["email"])
        login_data.add_field('password', self.user_data["password"])

        async with self.session.post(
            f"{self.base_url}/auth/login",
            data=login_data
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.access_token = data.get("access_token")
                logger.info(f"✅ Login successful! Token: {self.access_token[:20]}...")
                return True
            else:
                error = await response.text()
                logger.error(f"❌ Login failed: {error}")
                return False

    async def test_feedback_basic(self) -> bool:
        """Test basic feedback endpoint without market research"""
        logger.info("\n📊 Testing basic feedback endpoint...")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        request_data = {
            "enable_market_research": False
        }

        async with self.session.post(
            f"{self.base_url}/ai/feedback/analyze",
            json=request_data,
            headers=headers
        ) as response:
            logger.info(f"Response status: {response.status}")

            if response.status == 200:
                data = await response.json()
                logger.info(f"✅ Basic feedback received!")
                logger.info(f"   Overall Score: {data['overall_score']}/100")
                logger.info(f"   Summary: {data['summary'][:100]}...")
                logger.info(f"   Skills Analyzed: {len(data['skills_analysis'])}")
                logger.info(f"   Recommendations: {len(data['top_recommendations'])}")
                return True
            else:
                error = await response.text()
                logger.error(f"❌ Basic feedback failed: {error}")
                return False

    async def test_feedback_with_market_research(self) -> bool:
        """Test feedback endpoint with market research"""
        logger.info("\n🌐 Testing feedback with market research...")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        request_data = {
            "enable_market_research": True
        }

        async with self.session.post(
            f"{self.base_url}/ai/feedback/analyze",
            json=request_data,
            headers=headers
        ) as response:
            logger.info(f"Response status: {response.status}")

            if response.status == 200:
                data = await response.json()
                logger.info(f"✅ Market-enhanced feedback received!")
                logger.info(f"   Overall Score: {data['overall_score']}/100")
                logger.info(f"   Summary: {data['summary'][:100]}...")
                logger.info(f"   Market Alignment: {data.get('market_alignment', 'N/A')[:100] if data.get('market_alignment') else 'N/A'}...")
                logger.info(f"   Skills Analyzed: {len(data['skills_analysis'])}")
                logger.info(f"   Recommendations: {len(data['top_recommendations'])}")

                # Save detailed response
                with open('endpoint_feedback_results.json', 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info("💾 Detailed results saved to: endpoint_feedback_results.json")

                return True
            else:
                error = await response.text()
                logger.error(f"❌ Market research feedback failed: {error}")
                return False

    async def test_unauthorized_access(self) -> bool:
        """Test that endpoints require authentication"""
        logger.info("\n🚫 Testing unauthorized access...")

        request_data = {
            "enable_market_research": False
        }

        async with self.session.post(
            f"{self.base_url}/ai/feedback/analyze",
            json=request_data
            # No Authorization header
        ) as response:
            if response.status == 401:
                logger.info("✅ Correctly rejected unauthorized request")
                return True
            else:
                logger.error(f"❌ Should have rejected unauthorized request, got {response.status}")
                return False

    async def run_complete_test(self):
        """Run complete endpoint test suite"""
        logger.info(f"\n🎯 TESTING AI FEEDBACK ENDPOINTS")
        logger.info(f"Target: {self.base_url}")
        logger.info(f"Time: {datetime.now().isoformat()}")
        logger.info("=" * 60)

        # Test unauthorized access first
        unauthorized_ok = await self.test_unauthorized_access()

        # Login
        login_success = await self.login()
        if not login_success:
            logger.error("❌ Cannot proceed without login")
            return

        # Test authenticated endpoints
        basic_success = await self.test_feedback_basic()
        market_success = await self.test_feedback_with_market_research()

        # Summary
        logger.info(f"\n📊 TEST SUMMARY:")
        logger.info(f"   Unauthorized rejection: {'✅' if unauthorized_ok else '❌'}")
        logger.info(f"   Login success: {'✅' if login_success else '❌'}")
        logger.info(f"   Basic feedback: {'✅' if basic_success else '❌'}")
        logger.info(f"   Market research feedback: {'✅' if market_success else '❌'}")

        total_tests = 4
        passed_tests = sum([unauthorized_ok, login_success, basic_success, market_success])
        logger.info(f"   Overall: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            logger.info("🎉 All tests passed! Endpoints are working correctly.")
        else:
            logger.warning(f"⚠️ {total_tests - passed_tests} test(s) failed.")

async def main():
    """Main test execution"""
    async with FeedbackEndpointTester() as tester:
        await tester.run_complete_test()

if __name__ == "__main__":
    asyncio.run(main())