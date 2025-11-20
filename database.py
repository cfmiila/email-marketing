from sqlalchemy import Column, create_engine, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()
engine = create_engine('sqlite:///emails.db')
Session = sessionmaker(bind=engine)

class Email(Base):
    __tablename__ = 'emails'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

Base.metadata.create_all(engine)

def add_email(address):
    session = Session()
    new_email = Email(email=address)
    try:
        session.add(new_email)
        session.commit()
        return True, "E-mail adicionado com sucesso!"
    except IntegrityError:
        session.rollback()
        return False, "Esse e-mail já está cadastrado."
    except Exception as e:
        session.rollback()
        return False, f"Erro inesperado: {str(e)}"
    finally:
        session.close()

def remove_email(address):
    session = Session()
    email = session.query(Email).filter_by(email=address).first()
    if email:
        session.delete(email)
        session.commit()
    session.close()

def update_email(old_address, new_address):
    session = Session()
    email = session.query(Email).filter_by(email=old_address).first()
    if email:
        email.email = new_address
        session.commit()
    session.close()

def get_emails():
    session = Session()
    emails = [(e.id, e.email) for e in session.query(Email).all()]
    session.close()
    return emails
