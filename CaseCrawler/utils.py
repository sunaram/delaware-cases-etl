from datetime import datetime
from xmlrpc.client import DateTime
from sqlalchemy.orm import sessionmaker
from CaseCrawler.models import ErrorLog, db_connect, create_table
import logging

class Utils:
    def __init__(self):
        #initialize db 
        engine = db_connect()
        # create tables
        create_table(engine)
        # session
        self.Session = sessionmaker(bind = engine)
    
    def insert_error_log(self, error_log_dict):
        session = self.Session()
        error_log = ErrorLog(url = error_log_dict.get("url"), error_type = error_log_dict.get("error_type"), error_message = error_log_dict.get("error_message"), created = datetime.now())
        
        try:
            session.add(error_log)
            session.commit()
        except:
            logging.error("Error encountered while trying to log an error message")
        finally:
            session.close()