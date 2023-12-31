from sqlalchemy import String, Date, Column, Integer, ForeignKey, Boolean

from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    email = Column(String(150), index=True, unique=True)
    phone = Column(String(17))
    birthday = Column(Date)
    other = Column(String)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship("User", backref="contacts", lazy="joined")


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), index=True)
    email = Column(String(150), index=True, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(250), nullable=True)
    confirmed = Column(Boolean, default=False, nullable=True)
    avatar = Column(String(250), nullable=True)

