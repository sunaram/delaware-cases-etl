from sqlalchemy import create_engine, Column, Table, ForeignKey, UniqueConstraint, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings
import os 
import logging

Base = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    connection_string = os.environ.get("CONNECTION_STRING") if os.environ.get("CONNECTION_STRING") is not None else get_project_settings().get("CONNECTION_STRING")
    return create_engine(connection_string)

def create_table(engine):
    Base.metadata.create_all(engine)

class DelawareCase(Base):
    __tablename__ = "delaware_cases"

    case_id = Column(String(25), primary_key = True)
    case_title = Column(String(255))
    filing_date = Column(Date)
    case_status = Column(String(50))
    created = Column(DateTime)
    parties = relationship('DelawareParty', secondary = 'delaware_case_party')
    dockets = relationship('DelwareCaseDocket', backref = 'delaware_cases')
    associations = relationship('DelawareCasePartyAssociation', backref = 'delaware_cases')

class DelawareParty(Base):
    __tablename__ = "delaware_parties"

    party_id = Column(String(25), primary_key = True, nullable = False)
    party_name = Column(String(255))
    address = Column(Text())
    cases = relationship('DelawareCase', secondary = 'delaware_case_party')

class DelawareCaseParty(Base):
    __tablename__ = "delaware_case_party"

    case_id = Column(String(25), ForeignKey('delaware_cases.case_id'),primary_key = True, nullable = False)
    party_id = Column(String(25), ForeignKey('delaware_parties.party_id'),primary_key = True, nullable = False)
    party_type = Column(String(50))
    party_end_date = Column(Date, nullable = True)

class DelwareCaseDocket(Base):
    __tablename__ = "delaware_case_dockets"
    __table_args__ = (
        UniqueConstraint('case_id', 'entry_date_time', name='case_entry_time'),
    )

    id = Column(Integer, primary_key = True, autoincrement = True)
    case_id = Column(String(25), ForeignKey('delaware_cases.case_id'), nullable = False)
    entry_date_time = Column(DateTime, nullable = False)
    description = Column(Text())
    name = Column(String(255))
    monetary = Column(String(255))
    entry = Column(Text())

class DelawareCasePartyAssociation(Base):
    __tablename__ = "delaware_case_party_associations"

    case_id = Column(String(25), ForeignKey('delaware_cases.case_id'), primary_key = True, nullable = False)
    party_id = Column(String(25), primary_key = True, nullable = False)
    other_party_id = Column(String(25), primary_key = True, nullable = False) 

class ErrorLog(Base):
    __tablename__ = "error_log"

    id = Column(Integer, primary_key = True, autoincrement = True)
    url = Column(Text(), nullable = False)
    error_type = Column(String(100))
    error_message = Column(Text())
    created = Column(DateTime)
