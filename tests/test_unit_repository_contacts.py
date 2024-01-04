import unittest
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema
from src.repository.contacts import create_contact, get_contacts, update_contact, delete_contact


class TestAsyncContact(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username='test_user', password="qwerty", email='test@email.com')
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [Contact(id=1, first_name='test_first_name_1', last_name='test_last_name_1', email='test@email.com_1',
                            phone='test_phone_1', birthday='2021-01-01', user=self.user),
                    Contact(id=2, first_name='test_first_name_2', last_name='test_last_name_2', email='test@email.com_2',
                            phone='test_phone_1', birthday='2021-01-02', user=self.user)]
        mocked_contacts = Mock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        body = ContactSchema(first_name='test_first_name', last_name='test_last_name', email='test@email.com',
                             phone='test_phone', birthday='2021-01-01', other='test_other')
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)

    async def test_update_contact(self):
        body = ContactSchema(first_name='test_first_name', last_name='test_last_name', email='test@email.com',
                             phone='test_phone', birthday='2021-01-01', other='test_other')
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, first_name='test_first_name',
                                                                 last_name='test_last_name', email='test@email.com',
                                                                 phone='test_phone', birthday='2021-01-01',
                                                                 user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await update_contact(1, body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)

    async def test_delete_contact(self):
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(id=1, first_name='test_first_name',
                                                                 last_name='test_last_name', email='test@email.com',
                                                                 phone='test_phone', birthday='2021-01-01',
                                                                 user=self.user)
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, Contact)
