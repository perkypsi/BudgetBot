from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String, VARCHAR
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from enum import Enum

class TypeTransaction(Enum):
    INCOME = 0
    OUTCOME = 1

Base = declarative_base()
engine = create_engine('sqlite:///budget.db')

class Person(Base):
    __tablename__ = 'PERSON'
    id = Column(Integer, primary_key=True)
    username = Column(VARCHAR(100))
    last_name = Column(VARCHAR(100))
    first_name = Column(VARCHAR(100))
    patronymic = Column(VARCHAR(100))
    description = Column(VARCHAR(1000))

class Category(Base):
    __tablename__ = 'CATEGORY'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(100))


class Transaction(Base):
    __tablename__ = 'TRANSACTION'
    id = Column(Integer, primary_key=True)
    description = Column(VARCHAR(10000))
    date = Column(DateTime)
    account = Column(Integer, ForeignKey(Person.id))
    volume = Column(Numeric)
    category = Column(Integer, ForeignKey(Category.id))
    type_transaction = Column(Integer)

class Account(Base):
    __tablename__ = 'ACCOUNT'
    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(100))
    description = Column(VARCHAR(10000))
    type_account = Column(Integer, default=0)
    balance = Column(Numeric)
    owner = Column(Integer, ForeignKey(Person.id))

class Debt(Base):
    __tablename__ = 'DEBT'
    id = Column(Integer, primary_key=True)
    debtor = Column(Integer, ForeignKey(Person.id))
    recipient = Column(Integer, ForeignKey(Person.id))
    volume = Column(Numeric)
    date = Column(DateTime)
    state = Column(Integer, default=0)
    description = Column(VARCHAR(10000))



Base.metadata.create_all(engine)

def addCategory(name: str):
    session = Session(engine)
    category = Category(name=name)
    session.add(category)
    session.commit()

def printCategory():
    session = Session(engine)
    categories = session.query(Category).all()
    return categories

def delCategory(name):
    session = Session(engine)
    category_to_delete = session.query(Category).filter_by(name=name).first()
    session.delete(category_to_delete)
    session.commit()


def addIncome(description: str, date, volume, category):
    session = Session(engine)
    transaction = Transaction(description=description, date=date, volume=volume, category=category, type_transaction=TypeTransaction.INCOME.value)
    session.add(transaction)
    session.commit()

def addOutcome(description: str, date, volume, category):
    session = Session(engine)
    transaction = Transaction(description=description, date=date, volume=volume, category=category, type_transaction=TypeTransaction.OUTCOME.value)
    session.add(transaction)
    session.commit()
# person = Person(username='person1', last_name="PERSON", first_name='Person', patronymic='PeRsOn', description='text text text')
# session.add(person)
# session.commit()
# account = Account(name='kredit', description='кредит кредит кредит', type_account=0, balance=123.43, owner=person.id)
# session.add(account)
# session.commit()
