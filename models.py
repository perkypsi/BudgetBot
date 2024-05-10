from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String, VARCHAR
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from enum import Enum
import pandas as pd
from io import BytesIO

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

# ФУНКЦИИ КАТЕГОРИЙ

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

# Формирование таблицы транзакций:
    
def create_transaction_table():
    session = Session(engine)
    transactions = session.query(Transaction).all()
    debts = session.query(Debt).all()

    data_debts = {
        'ID': [t.id for t in debts],
        'Должник': [f"{session.query(Person).filter_by(id=t.debtor).first().last_name} {session.query(Person).filter_by(id=t.debtor).first().first_name}" for t in debts],
        'Кому должен': [f"{session.query(Person).filter_by(id=t.recipient).first().last_name} {session.query(Person).filter_by(id=t.recipient).first().first_name}" for t in debts],
        'Сумма': [t.volume for t in debts],
        'Дата долга': [t.date for t in debts],
        'Описание': [t.description for t in debts],
        'Статус': ['Оплачен' if t.state else 'Не закрыт' for t in debts],
    }
    data_trans = {
        'ID': [t.id for t in transactions],
        'Описание': [t.description for t in transactions],
        'Дата транзакции': [t.date for t in transactions],
        'Сумма': [t.volume for t in transactions],
        'Категория': [t.category for t in transactions],
        'Тип транзакции': ['Расход' if t.type_transaction else 'Доход' for t in transactions]
    }
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        pd.DataFrame(data_trans).to_excel(writer, sheet_name='Transactions', index=False)
        pd.DataFrame(data_debts).to_excel(writer, sheet_name='Debts', index=False)
    
    return buffer


# ФУНКЦИИ ДОХОДА

def addIncome(description: str, date, volume, category):
    session = Session(engine)
    transaction = Transaction(description=description, date=date, volume=volume, category=category, type_transaction=TypeTransaction.INCOME.value)
    session.add(transaction)
    session.commit()

def getIncomes():
    session = Session(engine)
    incomes = session.query(Transaction).filter_by(type_transaction=TypeTransaction.INCOME.value).order_by(Transaction.id.desc()).limit(10)
    return incomes


def delIncome(id: int):
    session = Session(engine)
    transaction = session.query(Transaction).filter_by(id=id, type_transaction=TypeTransaction.INCOME.value).first()
    session.delete(transaction)
    session.commit()

# ФУНКЦИИ РАСХОДА
    
def addOutcome(description: str, date, volume, category):
    session = Session(engine)
    transaction = Transaction(description=description, date=date, volume=volume, category=category, type_transaction=TypeTransaction.OUTCOME.value)
    session.add(transaction)
    session.commit()

def getOutcomes():
    session = Session(engine)
    outcomes = session.query(Transaction).filter_by(type_transaction=TypeTransaction.OUTCOME.value).order_by(Transaction.id.desc()).limit(10)
    return outcomes

def delOutcome(id: int):
    session = Session(engine)
    transaction = session.query(Transaction).filter_by(id=id, type_transaction=TypeTransaction.OUTCOME.value).first()
    session.delete(transaction)
    session.commit()

# ФУНКЦИИ ДОЛГОВ
    
def addDebt(debtor, recipient, volume, date, description):
    session = Session(engine)
    new_debt = Debt(debtor=debtor, recipient=recipient, volume=volume, date=date, description=description)
    session.add(new_debt)
    session.commit()

def getDebts():
    session = Session(engine)
    debts = session.query(Debt).filter_by(state=0).order_by(Debt.id.desc()).limit(10)
    return debts

def payDebt(id):
    session = Session(engine)
    choisen_debt = session.query(Debt).filter_by(id=id).first()
    choisen_debt.state = 1
    session.commit()

def delDebt(id):
    session = Session(engine)
    choisen_debt = session.query(Debt).filter_by(id=id).first()
    session.delete(choisen_debt)
    session.commit()

# ФУНКЦИИ ПЕРСОН

def addPerson(username, last_name, first_name, patronymic, description):
    session = Session(engine)
    new_person = Person(username=username, last_name=last_name, first_name=first_name, patronymic=patronymic, description=description)
    session.add(new_person)
    session.commit()

def printPersons():
    session = Session(engine)
    persons = session.query(Person).all()
    return persons

def getPersons():
    session = Session(engine)
    persons = session.query(Person).order_by(Person.id.desc()).limit(10)
    return persons

def getPerson(username):
    session = Session(engine)
    person = session.query(Person).filter_by(username=username).first()
    return person

def delPerson(id):
    session = Session(engine)
    choisen_person = session.query(Person).filter_by(id=id).first()
    session.delete(choisen_person)
    session.commit()