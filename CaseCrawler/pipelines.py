# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from itemadapter import ItemAdapter
from CaseCrawler.items import DelawareItem
from sqlalchemy import and_, or_
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from CaseCrawler.models import DelawareCase, DelawareParty, DelawareCaseParty, DelwareCaseDocket, DelawareCasePartyAssociation, db_connect, create_table
import logging

class CasecrawlerPipeline:
    def __init__(self):
        #initialize db 
        engine = db_connect()
        # create tables
        create_table(engine)
        # session
        self.Session = sessionmaker(bind = engine)

    def process_item(self, item, spider):
        # process items based on the item type
        if isinstance(item, DelawareItem):
            return self.process_delaware_item(item, spider)
        else:
            return item

    def process_delaware_item(self, item, spider):
        # insert into database
        session = self.Session()
        # process delaware case  
        # check whether the case already exists
        exist_case = session.query(DelawareCase).filter_by(case_id = item["case_id"]).first()
        if exist_case is None:
            # add it to the db
            delaware_case = DelawareCase()
            delaware_case.case_id = item.get("case_id")
            delaware_case.case_title = item.get("case_title", "")
            delaware_case.filing_date = item.get("filing_date")
            delaware_case.case_status = item.get("case_status", "")
            delaware_case.created = datetime.now()
            try:
                session.add(delaware_case)
                session.commit()
            except:
                logging.error("Error encountered while adding delaware case: "+ item["case_id"])
            
        # process case party        
        party = DelawareParty(party_id = item.get("id"), party_name = item.get("party_name", ""), address = item.get("address", ""))
        case_party = DelawareCaseParty(case_id = item.get("case_id"), party_id = item.get("id"), party_type = item.get("party_type", ""), party_end_date = item.get("party_end_date"))
        self.process_delaware_case_party(session, party, case_party)
        # process extra parties, if available
        for party_item in item["extra_parties"]:
            party = DelawareParty(party_id = party_item.get("id"), party_name = party_item.get("name", ""), address = party_item.get("address", ""))
            case_party = DelawareCaseParty(case_id = item.get("case_id"), party_id = party_item.get("id"), party_type = party_item.get("type", ""))
            self.process_delaware_case_party(session, party, case_party)

        # process dockets
        for docket_entry in item["docket_entries"]:
            # check if the docket entry already exists
            exist_docket = session.query(DelwareCaseDocket).filter_by(case_id = item.get("case_id"), entry_date_time = docket_entry.get("date_time")).first()
            if exist_docket is None:
                #add to the db
                delaware_case_docket = DelwareCaseDocket(case_id = item.get("case_id"), entry_date_time = docket_entry.get("date_time"), description = docket_entry.get("description", ""), name = docket_entry.get("name", ""), monetary = docket_entry.get("monetary", ""), entry = docket_entry.get("complete_entry", ""))
                try:
                    session.add(delaware_case_docket)
                    session.commit()
                except:
                    logging.error("Error encountered while adding delaware case docket entry: "+ docket_entry.get("description", ""))
        
        # process party associations
        for association in item["associations"]:
            keys = association.keys()
            if(len(keys) < 1):
                continue
            party_id = list(keys)[0]
            other_party_id = association[party_id]
            # check if the association already exists
            query = session.query(DelawareCasePartyAssociation).filter(or_(
                (and_(DelawareCasePartyAssociation.party_id == party_id, DelawareCasePartyAssociation.other_party_id == other_party_id, DelawareCasePartyAssociation.case_id == item.get("case_id"))),
                (and_(DelawareCasePartyAssociation.party_id == other_party_id, DelawareCasePartyAssociation.other_party_id == party_id, DelawareCasePartyAssociation.case_id == item.get("case_id")))
            ))
            exist_association = query.first()
            if exist_association is None:
                # add it to the db
                delaware_case_party_association = DelawareCasePartyAssociation(party_id = party_id, other_party_id = other_party_id, case_id = item.get("case_id"))
                try:
                    session.add(delaware_case_party_association)
                    session.commit()
                except:
                    logging.error("Error encountered while adding delaware case party association: ("+ party_id +", "+ other_party_id +")")

        # return item
        return item
    
    # processes a party record
    def process_delaware_case_party(self, session, party, case_party):
        exist_party = session.query(DelawareParty).filter_by(party_id = party.party_id).first()
        if exist_party is None:
            # add the party to the db
            try:
                session.add(party)
                session.commit()
            except:
                logging.error("Error encountered while adding delaware  party: "+ party.party_id)
        exist_case_party = session.query(DelawareCaseParty).filter_by(case_id = case_party.case_id, party_id = case_party.party_id).first()
        if exist_case_party is None:
            # add the case party association to the db
            try:
                session.add(case_party)
                session.commit()
            except:
                logging.error("Error encountered while adding delaware case party: "+ case_party.case_id +", "+ case_party.party_id)