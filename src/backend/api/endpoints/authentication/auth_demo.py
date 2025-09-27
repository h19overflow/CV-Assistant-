"""
Authentication API Demo with Full Observability
Demonstrates all authentication endpoints with comprehensive logging and error handling.
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('auth_demo.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AuthResponse:
    """Response tracking for observability"""
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    headers: Optional[Dict[str, str]] = None

class AuthDemo:
    """
    Authentication API demonstration with full observability.
    Tests all endpoints from the PlantUML sequence diagram.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
        self.user_data = {
            "email": "demo@example.com",
            "password": "SecurePassword123!"
        }
        self.responses: list[AuthResponse] = []

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        auth_required: bool = False
    ) -> AuthResponse:
        """
        Make HTTP request with full observability tracking.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            headers: Additional headers
            auth_required: Whether to include JWT token

        Returns:
            AuthResponse with complete request/response information
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            **(headers or {})
        }

        # Add authorization if required
        if auth_required and self.access_token:
            request_headers["Authorization"] = f"Bearer {self.access_token}"

        logger.info(f"🚀 {method} {endpoint}")
        logger.debug(f"Headers: {request_headers}")
        if data:
            logger.debug(f"Request body: {json.dumps(data, indent=2)}")

        try:
            # Handle form data for OAuth2 login
            if endpoint == "/auth/login":
                form_data = aiohttp.FormData()
                form_data.add_field('username', data['username'])
                form_data.add_field('password', data['password'])

                async with self.session.request(
                    method, url, data=form_data, headers={k: v for k, v in request_headers.items() if k != "Content-Type"}
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()

                    auth_response = AuthResponse(
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status,
                        response_time_ms=response_time,
                        success=response.status < 400,
                        data=response_data if response.status < 400 else None,
                        error=str(response_data) if response.status >= 400 else None,
                        headers=dict(response.headers)
                    )
            else:
                # Regular JSON requests
                async with self.session.request(
                    method, url, json=data, headers=request_headers
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    response_data = await response.json() if response.content_type == 'application/json' else await response.text()

                    auth_response = AuthResponse(
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status,
                        response_time_ms=response_time,
                        success=response.status < 400,
                        data=response_data if response.status < 400 else None,
                        error=str(response_data) if response.status >= 400 else None,
                        headers=dict(response.headers)
                    )

            # Log response details
            status_emoji = "✅" if auth_response.success else "❌"
            logger.info(f"{status_emoji} {auth_response.status_code} - {response_time:.1f}ms")

            if auth_response.success and auth_response.data:
                logger.info(f"Response: {json.dumps(auth_response.data, indent=2)}")
            elif auth_response.error:
                logger.error(f"Error: {auth_response.error}")

            self.responses.append(auth_response)
            return auth_response

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_response = AuthResponse(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time_ms=response_time,
                success=False,
                error=f"Request failed: {str(e)}"
            )
            logger.error(f"❌ Request failed: {e}")
            self.responses.append(error_response)
            return error_response

    async def test_user_registration(self) -> bool:
        """
        Test user registration endpoint.
        Follows PlantUML: Client -> API: POST /auth/register
        """
        logger.info("\n🔧 TESTING USER REGISTRATION")
        logger.info("=" * 50)

        response = await self.make_request(
            "POST",
            "/auth/register",
            data=self.user_data
        )

        if response.success:
            logger.info(f"✅ User registered successfully: {response.data}")
            return True
        else:
            if "already exists" in str(response.error).lower():
                logger.warning("⚠️ User already exists - continuing with existing user")
                return True
            else:
                logger.error(f"❌ Registration failed: {response.error}")
                return False

    async def test_user_login(self) -> bool:
        """
        Test user login endpoint with OAuth2 form.
        Follows PlantUML: Client -> API: POST /auth/login
        """
        logger.info("\n🔑 TESTING USER LOGIN")
        logger.info("=" * 50)

        # OAuth2PasswordRequestForm expects 'username' field
        login_data = {
            "username": self.user_data["email"],  # OAuth2 standard uses 'username'
            "password": self.user_data["password"]
        }

        response = await self.make_request(
            "POST",
            "/auth/login",
            data=login_data
        )

        if response.success and response.data:
            self.access_token = response.data.get("access_token")
            logger.info(f"✅ Login successful! Token: {self.access_token[:20]}...")
            logger.info(f"User ID: {response.data.get('user_id')}")
            logger.info(f"Email: {response.data.get('email')}")
            return True
        else:
            logger.error(f"❌ Login failed: {response.error}")
            return False

    async def test_get_current_user(self) -> bool:
        """
        Test getting current user information.
        Follows PlantUML: Client -> API: GET /auth/me (with JWT token)
        """
        logger.info("\n👤 TESTING GET CURRENT USER")
        logger.info("=" * 50)

        if not self.access_token:
            logger.error("❌ No access token available")
            return False

        response = await self.make_request(
            "GET",
            "/auth/me",
            auth_required=True
        )

        if response.success:
            logger.info(f"✅ Current user retrieved: {response.data}")
            return True
        else:
            logger.error(f"❌ Failed to get current user: {response.error}")
            return False

    async def test_verify_token(self) -> bool:
        """
        Test token verification endpoint.
        Follows PlantUML: Client -> API: POST /auth/verify-token (with JWT token)
        """
        logger.info("\n🔍 TESTING TOKEN VERIFICATION")
        logger.info("=" * 50)

        if not self.access_token:
            logger.error("❌ No access token available")
            return False

        response = await self.make_request(
            "POST",
            "/auth/verify-token",
            auth_required=True
        )

        if response.success:
            logger.info(f"✅ Token verified: {response.data}")
            return True
        else:
            logger.error(f"❌ Token verification failed: {response.error}")
            return False

    async def test_invalid_token_scenarios(self):
        """Test various invalid token scenarios for comprehensive coverage"""
        logger.info("\n🚫 TESTING INVALID TOKEN SCENARIOS")
        logger.info("=" * 50)

        # Test expired/invalid token
        original_token = self.access_token
        self.access_token = "invalid.jwt.token"

        logger.info("Testing with invalid token...")
        await self.make_request("GET", "/auth/me", auth_required=True)
        await self.make_request("POST", "/auth/verify-token", auth_required=True)

        # Test no token
        self.access_token = None
        logger.info("Testing with no token...")
        await self.make_request("GET", "/auth/me", auth_required=True)

        # Restore valid token
        self.access_token = original_token

    async def run_complete_demo(self):
        """Run complete authentication flow demo with full observability"""
        logger.info(f"\n🎯 STARTING AUTHENTICATION API DEMO")
        logger.info(f"Target: {self.base_url}")
        logger.info(f"Time: {datetime.now().isoformat()}")
        logger.info("=" * 70)

        # Test all endpoints in sequence
        registration_success = await self.test_user_registration()

        if registration_success:
            login_success = await self.test_user_login()

            if login_success:
                await self.test_get_current_user()
                await self.test_verify_token()
                await self.test_invalid_token_scenarios()

        # Generate comprehensive report
        await self.generate_observability_report()

    async def generate_observability_report(self):
        """Generate comprehensive observability report"""
        logger.info("\n📊 OBSERVABILITY REPORT")
        logger.info("=" * 70)

        total_requests = len(self.responses)
        successful_requests = sum(1 for r in self.responses if r.success)
        failed_requests = total_requests - successful_requests
        avg_response_time = sum(r.response_time_ms for r in self.responses) / total_requests if total_requests > 0 else 0

        logger.info(f"📈 SUMMARY METRICS:")
        logger.info(f"   Total Requests: {total_requests}")
        logger.info(f"   Successful: {successful_requests} ({successful_requests/total_requests*100:.1f}%)")
        logger.info(f"   Failed: {failed_requests} ({failed_requests/total_requests*100:.1f}%)")
        logger.info(f"   Average Response Time: {avg_response_time:.1f}ms")

        logger.info(f"\n📋 DETAILED RESULTS:")
        for i, response in enumerate(self.responses, 1):
            status_emoji = "✅" if response.success else "❌"
            logger.info(f"   {i:2d}. {status_emoji} {response.method:4s} {response.endpoint:20s} "
                       f"{response.status_code:3d} {response.response_time_ms:6.1f}ms")

        # Endpoint performance analysis
        logger.info(f"\n⚡ ENDPOINT PERFORMANCE:")
        endpoint_stats = {}
        for response in self.responses:
            key = f"{response.method} {response.endpoint}"
            if key not in endpoint_stats:
                endpoint_stats[key] = []
            endpoint_stats[key].append(response.response_time_ms)

        for endpoint, times in endpoint_stats.items():
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            logger.info(f"   {endpoint:30s} avg: {avg_time:6.1f}ms min: {min_time:6.1f}ms max: {max_time:6.1f}ms")

        # Save detailed report to file
        report_data = {
            "summary": {
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "avg_response_time_ms": avg_response_time,
                "test_timestamp": datetime.now().isoformat()
            },
            "responses": [asdict(r) for r in self.responses],
            "endpoint_performance": {
                endpoint: {
                    "avg_ms": sum(times) / len(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                    "count": len(times)
                }
                for endpoint, times in endpoint_stats.items()
            }
        }

        with open('auth_demo_report.json', 'w') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"\n💾 Detailed report saved to: auth_demo_report.json")
        logger.info(f"📝 Logs saved to: auth_demo.log")

async def main():
    """Main demo execution"""
    async with AuthDemo() as demo:
        await demo.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())