# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import json
from scrapy import Item, Field
from scrapy.loader.processors import MapCompose, TakeFirst
from datetime import datetime

def convert_date(text):
    try:
        return datetime.strptime(text, '%d-%b-%Y')
    except:
        return None
        
def process_entry_list(entries):
    new_entries = []
    for entry in json.loads(entries):
        if entry["date_time"].strip() == "":
            continue 
        entry["date_time"] = datetime.strptime(entry["date_time"], '%d-%b-%Y %I:%M %p')
        new_entries.append(entry)
    return new_entries

class DelawareItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = Field(
        input_processor = MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    party_name = Field(
        input_processor = MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    case_id = Field(
        input_processor = MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    case_title = Field(
        input_processor = MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    address = Field(
        input_processor = MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    party_type = Field(
        input_processor = MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    party_end_date = Field(
        input_processor = MapCompose(str.strip, convert_date),
        output_processor = TakeFirst()
    )
    filing_date = Field(
        input_processor = MapCompose(str.strip, convert_date),
        output_processor = TakeFirst()
    )
    case_status = Field(
        input_processor = MapCompose(str.strip),
        output_processor = TakeFirst()
    )
    docket_entries = Field(
        input_processor = MapCompose(process_entry_list)
    )
    associations = Field()
    extra_parties = Field()
