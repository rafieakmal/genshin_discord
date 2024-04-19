import hashlib
import os
import base64
import asyncio

class HasherHelper:
    @staticmethod
    async def generate_salt(length=16):
        """Generate a random salt for hashing."""
        # Using os.urandom for generating a secure random salt
        return os.urandom(length)

    @staticmethod
    async def hash_string(password, salt=None):
        """
        Hash a password using SHA-256 with a provided salt.
        
        Args:
            password (str): The password to hash.
            salt (bytes, optional): The salt to use for hashing. If not provided, a new salt is generated.
            
        Returns:
            tuple: A tuple containing the salt and the hashed password.
        """
        if salt is None:
            salt = await HasherHelper.generate_salt()
        # Ensure the password is bytes
        if isinstance(password, str):
            password = password.encode('utf-8')
        # Hashing the password with the salt using SHA-256
        hasher = hashlib.pbkdf2_hmac('sha256', password, salt, 100000)
        # Returning the salt and the hashed password
        return salt, hasher

    @staticmethod
    async def verify_hash(stored_password, provided_password, salt):
        """
        Verify a provided password against one stored.
        
        Args:
            stored_password (bytes): The hashed password that is stored.
            provided_password (str): The password to verify.
            salt (bytes): The salt used to hash the stored password.
            
        Returns:
            bool: True if the passwords match, False otherwise.
        """
        # Hash the provided password with the stored salt
        _, hashed_provided_password = await HasherHelper.hash_string(provided_password, salt)
        # Compare the stored password with the hashed provided password
        return stored_password == hashed_provided_password
