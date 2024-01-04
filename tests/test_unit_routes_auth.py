import unittest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from src.routes.auth import refresh_token


class TestRefreshTokenEndpoint(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.token = "valid_token"
        self.invalid_token = "invalid_token"
        self.email = "test@example.com"
        self.credentials = HTTPAuthorizationCredentials(credentials=self.token, scheme="Bearer")
        self.mock_db = AsyncMock()

    @patch('src.repository.users.get_user_by_email')
    @patch('src.services.auth.auth_service.decode_refresh_token')
    async def test_refresh_token_valid(self, mock_decode_refresh_token, mock_get_user_by_email):
        mock_decode_refresh_token.return_value = self.email
        user_mock = AsyncMock()
        user_mock.refresh_token = self.token
        mock_get_user_by_email.return_value = user_mock

        try:
            response = await refresh_token(credentials=self.credentials, db=AsyncMock())
        except HTTPException as e:
            self.fail(f"HTTPException was raised: {e.detail}")

        self.assertIsNotNone(response, "The response should not be None.")
        self.assertIn('access_token', response, "The response should include an 'access_token'.")
        self.assertIn('refresh_token', response, "The response should include a 'refresh_token'.")
        self.assertIn('token_type', response, "The response should include a 'token_type'.")
        self.assertEqual(response['token_type'], 'bearer', "The token type should be 'bearer'.")
        self.assertIsInstance(response['access_token'], str, "The access token should be a string.")
        self.assertIsInstance(response['refresh_token'], str, "The refresh token should be a string.")
        self.assertNotEqual(response['access_token'], response['refresh_token'],
                            "The new access token should be different from the refresh token.")
        self.assertEqual(response['refresh_token'], user_mock.refresh_token,
                         "The returned refresh token should match the user's refresh token.")

    @patch('src.repository.users.get_user_by_email')
    @patch('src.services.auth.Auth.decode_refresh_token')
    async def test_refresh_token_invalid(self, mock_decode_refresh_token, mock_get_user_by_email):
        mock_decode_refresh_token.return_value = self.email
        mock_user = AsyncMock()
        mock_user.refresh_token = self.invalid_token
        mock_get_user_by_email.return_value = mock_user

        with self.assertRaises(HTTPException) as context:
            await refresh_token(credentials=self.credentials, db=AsyncMock())

        self.assertEqual(context.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(context.exception.detail, "Invalid refresh token")


if __name__ == '__main__':
    unittest.main()
