import os
import sys
from sqlalchemy import Column, create_engine, ForeignKey, \
                        Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Category(Base):
    """Store category data

    Attributes:
        id: id for category (primary key)
        name: title of category
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)

    @property
    def serialize(self):
        """serialized category object for JSON endpoints"""
        return {
            'name': self.name,
            'id': self.id
        }


class User(Base):
    """store user data

    Attributes:
        id: id for user (primary key)
        name: name of user
        email: user email
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(300), nullable=False)

    @property
    def serialize(self):
        """serialized user object for JSON endpoints"""
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email
        }


class Item(Base):
    """Store item data

    Attributes:
        id: id for item (primary key)
        name: name of item
        description: item description
        created_date: creation date for item
        updated_date: last updated date for item
    """
    __tablename__ = 'item'

    name = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(300))
    created_date = Column(TIMESTAMP, nullable=False)
    updated_date = Column(TIMESTAMP)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

    @property
    def serialize(self):
        """serialized item object for JSON endpoints"""
        return {
            'item_name': self.name,
            'item_description': self.description,
            'item_id': self.id,
            'created_date': self.created_date,
            'updated_date': self.updated_date,
            'category_name': self.category.name,
            'user_email': self.user.email
        }


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
