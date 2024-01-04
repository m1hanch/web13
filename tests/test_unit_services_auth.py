import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from jose import jwt, JWTError
from fastapi import status

from src.services.auth import Auth
from src.services.email import send_email


class TestAuthMethods(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.auth = Auth()
        self.known_plain_password = "mysecretpassword"
        self.known_hashed_password = self.auth.pwd_context.hash(self.known_plain_password)
        self.test_secret_key = 'another_secret'
        self.test_algorithm = 'HS256'
        self.expires_delta = 600  # seconds, or adjust as needed for this case
        self.test_email = 'test_email'
        self.auth_instance = Auth()
        self.auth_instance.SECRET_KEY = self.test_secret_key
        self.auth_instance.ALGORITHM = self.test_algorithm
        self.test_host = 'testuser'
        self.test_username = "http://localhost:8000"

    def test_verify_password_correct(self):
        result = self.auth.verify_password(self.known_plain_password, self.known_hashed_password)
        self.assertTrue(result)

    def test_verify_password_incorrect(self):
        incorrect_password = "wrongpassword"
        result = self.auth.verify_password(incorrect_password, self.known_hashed_password)
        self.assertFalse(result)

    def test_get_password_hash(self):
        result = self.auth.get_password_hash(self.known_plain_password)
        self.assertIsInstance(result, str)

    @patch('src.services.auth.jwt.encode')
    async def test_create_refresh_token(self, mock_jwt_encode):
        # Setup your additional test case here
        test_data = {'user_id': 2}  # modify as needed for your new test case
        auth_instance = Auth()
        auth_instance.SECRET_KEY = self.test_secret_key
        auth_instance.ALGORITHM = self.test_algorithm
        # Expected payload setup for your additional test case
        expected_payload = test_data.copy()
        expected_payload.update({
            'exp': datetime.utcnow() + timedelta(seconds=self.expires_delta),
            'scope': 'refresh_token',
            'iat': datetime.utcnow()
        })

        # Mocked return value for jwt.encode in your additional test case
        mock_jwt_encode.return_value = 'another_test_token'

        # Execute the function
        token = await auth_instance.create_refresh_token(test_data, self.expires_delta)

        # Assertions for your additional test case
        mock_jwt_encode.assert_called_once_with(expected_payload, self.test_secret_key, algorithm=self.test_algorithm)
        self.assertEqual(token, 'another_test_token')

    @patch('src.services.auth.jwt.encode')
    async def test_create_access_token(self, mock_jwt_encode):
        test_data = {'user_id': 2}

        expected_payload = test_data.copy()
        expected_payload.update({
            'exp': datetime.utcnow() + timedelta(seconds=self.expires_delta),
            'scope': 'access_token',
            'iat': datetime.utcnow()
        })

        mock_jwt_encode.return_value = 'another_test_token'

        token = await self.auth_instance.create_access_token(test_data, self.expires_delta)

        mock_jwt_encode.assert_called_once_with(expected_payload, self.test_secret_key, algorithm=self.test_algorithm)
        self.assertEqual(token, 'another_test_token')

    async def test_decode_refresh_token_valid(self):
        """Test decoding a valid refresh token."""
        payload = {
            "sub": self.test_email,
            "scope": "refresh_token"
        }
        token = jwt.encode(payload, self.test_secret_key, algorithm=self.test_algorithm)

        email = await self.auth_instance.decode_refresh_token(refresh_token=token)
        self.assertEqual(email, self.test_email)

    async def test_decode_refresh_token_invalid_scope(self):
        """Test decoding a token with the wrong scope."""
        payload = {
            "sub": self.test_email,
            "scope": "wrong_scope"
        }
        token = jwt.encode(payload, self.test_secret_key, algorithm=self.test_algorithm)
        with self.assertRaises(HTTPException) as context:
            await self.auth_instance.decode_refresh_token(refresh_token=token)
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, 'Invalid scope for token')

    @patch('src.services.auth.jwt.decode', side_effect=JWTError)
    async def test_decode_refresh_token_invalid_token(self, mock_jwt_decode):
        test_data = {'user_id': 2}
        expected_payload = test_data.copy()
        expected_payload.update({
            'exp': datetime.utcnow() + timedelta(seconds=self.expires_delta),
            'scope': 'access_token',
            'iat': datetime.utcnow()
        })
        """Test decoding an invalid or expired token."""
        with self.assertRaises(HTTPException) as context:
            await self.auth_instance.decode_refresh_token(refresh_token="invalid_token")
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.detail, 'Could not validate credentials')



if __name__ == '__main__':
    unittest.main()
