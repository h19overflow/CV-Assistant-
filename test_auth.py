"""
Test script for authentication CRUD operations
"""

from src.backend.boundary.databases.db.CRUD.auth_CRUD import (
    AuthCRUD,
    create_user,
    login_user,
    get_user,
    UserAlreadyExistsError,
    InvalidCredentialsError
)


def test_authentication():
    """Test all authentication operations"""
    print("🔐 Testing Authentication CRUD Operations")
    print("=" * 50)

    test_email = "testuser@example.com"
    test_password = "secure_password_123"
    new_password = "new_secure_password_456"

    try:
        # Test 1: Create user
        print("\n1️⃣ Creating new user...")
        user = create_user(test_email, test_password)
        print(f"✅ Created user: {user.email} (ID: {user.id})")

        # Test 2: Try to create duplicate user (should fail)
        print("\n2️⃣ Testing duplicate user creation...")
        try:
            create_user(test_email, test_password)
            print("❌ Should have failed - duplicate user created!")
        except UserAlreadyExistsError:
            print("✅ Correctly prevented duplicate user creation")

        # Test 3: Authenticate with correct credentials
        print("\n3️⃣ Testing authentication with correct credentials...")
        authenticated_user = login_user(test_email, test_password)
        print(f"✅ Authentication successful: {authenticated_user.email}")

        # Test 4: Authenticate with wrong password
        print("\n4️⃣ Testing authentication with wrong password...")
        try:
            login_user(test_email, "wrong_password")
            print("❌ Should have failed - wrong password accepted!")
        except InvalidCredentialsError:
            print("✅ Correctly rejected wrong password")

        # Test 5: Authenticate with non-existent email
        print("\n5️⃣ Testing authentication with non-existent email...")
        try:
            login_user("nonexistent@example.com", test_password)
            print("❌ Should have failed - non-existent user authenticated!")
        except InvalidCredentialsError:
            print("✅ Correctly rejected non-existent user")

        # Test 6: Get user by ID
        print("\n6️⃣ Testing get user by ID...")
        retrieved_user = get_user(str(user.id))
        if retrieved_user and retrieved_user.email == test_email:
            print(f"✅ Retrieved user by ID: {retrieved_user.email}")
        else:
            print("❌ Failed to retrieve user by ID")

        # Test 7: Get user by email
        print("\n7️⃣ Testing get user by email...")
        user_by_email = AuthCRUD.get_user_by_email(test_email)
        if user_by_email and user_by_email.id == user.id:
            print(f"✅ Retrieved user by email: {user_by_email.email}")
        else:
            print("❌ Failed to retrieve user by email")

        # Test 8: Update password
        print("\n8️⃣ Testing password update...")
        success = AuthCRUD.update_password(str(user.id), test_password, new_password)
        if success:
            print("✅ Password updated successfully")

            # Verify old password no longer works
            try:
                login_user(test_email, test_password)
                print("❌ Old password still works!")
            except InvalidCredentialsError:
                print("✅ Old password correctly rejected")

            # Verify new password works
            new_auth_user = login_user(test_email, new_password)
            print(f"✅ New password authentication successful: {new_auth_user.email}")
        else:
            print("❌ Failed to update password")

        # Test 9: List users
        print("\n9️⃣ Testing list users...")
        users = AuthCRUD.list_users(limit=10)
        print(f"✅ Found {len(users)} user(s) in database")

        # Test 10: Delete user
        print("\n🔟 Testing user deletion...")
        deleted = AuthCRUD.delete_user(str(user.id))
        if deleted:
            print("✅ User deleted successfully")

            # Verify user no longer exists
            try:
                login_user(test_email, new_password)
                print("❌ Deleted user can still authenticate!")
            except InvalidCredentialsError:
                print("✅ Deleted user correctly cannot authenticate")
        else:
            print("❌ Failed to delete user")

        print("\n🎉 All authentication tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        # Cleanup: try to delete test user if it exists
        try:
            existing_user = AuthCRUD.get_user_by_email(test_email)
            if existing_user:
                AuthCRUD.delete_user(str(existing_user.id))
                print("🧹 Cleaned up test user")
        except:
            pass


def demo_usage():
    """Demonstrate typical usage patterns"""
    print("\n\n📚 Usage Examples")
    print("=" * 30)

    print("\n🔹 Creating a user:")
    print("user = create_user('john@example.com', 'secret123')")

    print("\n🔹 Logging in:")
    print("user = login_user('john@example.com', 'secret123')")

    print("\n🔹 Getting user info:")
    print("user = get_user(user_id)")
    print("user = AuthCRUD.get_user_by_email('john@example.com')")

    print("\n🔹 Changing password:")
    print("AuthCRUD.update_password(user_id, old_password, new_password)")

    print("\n🔹 Error handling:")
    print("""
try:
    user = login_user(email, password)
    print(f"Welcome {user.email}!")
except InvalidCredentialsError:
    print("Wrong email or password")
except UserAlreadyExistsError:
    print("User already exists")
    """)


if __name__ == "__main__":
    test_authentication()
    demo_usage()