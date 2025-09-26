from passlib.hash import pbkdf2_sha256


def hash_password(password: str) -> str:
    """Hash a password for storing."""
    return pbkdf2_sha256.hash(password)

if __name__ == "__main__":
    # Example usage
    plain_password = "my_secure_password"
    hashed = hash_password(plain_password)
    print(f"Plain: {plain_password}")
    print(f"Hashed: {hashed}")
    # Verify
    result = pbkdf2_sha256.verify(plain_password, hashed)
    print(result)