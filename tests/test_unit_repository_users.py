import unittest
from unittest.mock import AsyncMock, MagicMock, patch, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.user import UserSchema
from src.repository.users import get_user_by_email, create_user, update_token, confirmed_email, update_avatar_url, \
    update_password


class TestAsyncUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user_data = {
            'username': 'test_user',
            'email': 'test@email.com',
            'password': 'password',
            'avatar': 'https://example.com/avatar.png'
        }
        self.user = User(**self.user_data)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_user_by_email(self):
        self.session.execute.return_value.scalar_one_or_none = Mock(return_value=self.user)
        result = await get_user_by_email(self.user.email, self.session)
        self.assertEqual(result, self.user)

    async def test_create_user(self):
        user_schema = UserSchema(**self.user_data)
        self.session.add = MagicMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await create_user(user_schema, self.session)
        self.session.add.assert_called_once()
        self.session.commit.assert_awaited_once()
        self.assertIsInstance(result, User)
        self.assertEqual(result.username, user_schema.username)

    async def test_update_token(self):
        new_token = "newtoken123"
        await update_token(self.user, new_token, self.session)
        self.assertEqual(self.user.refresh_token, new_token)
        self.session.commit.assert_awaited_once()

    async def test_update_avatar_url(self):
        new_avatar_url = "https://newavatar.url"
        with patch('src.repository.users.get_user_by_email', new=AsyncMock(return_value=self.user)) as mock_get_user:
            result = await update_avatar_url(self.user.email, new_avatar_url, self.session)

            # Assertions
            self.assertEqual(result.avatar, new_avatar_url)
            self.session.commit.assert_awaited_once()

            # Ensure get_user_by_email was called with correct parameters
            mock_get_user.assert_awaited_once_with(self.user.email, self.session)

    async def test_update_password(self):
        new_password = "newpassword123"
        with patch('src.repository.users.get_user_by_email',
                   new=AsyncMock(return_value=self.user)) as mock_update_password:
            result = await update_password(self.user.email, new_password, self.session)
            self.assertEqual(result.password, new_password)
            self.session.commit.assert_awaited_once()
            mock_update_password.assert_awaited_once_with(self.user.email, self.session)


if __name__ == '__main__':
    unittest.main()
