import scrapy
from scrapy.loader import ItemLoader
import json
from datetime import datetime, timedelta
from CaseCrawler.items import DelawareItem
from CaseCrawler.utils import Utils
import string
import logging



class DelawareSpider(scrapy.Spider):
    name = "delaware"

    def __init__(self, days = 1, *args, **kargs) -> None:
        super(DelawareSpider, self).__init__(*args, **kargs)
        self.top_url = 'https://courtconnect.courts.delaware.gov/cc/cconnect/'
        from_date = datetime.now() - timedelta(days = int(days))
        self.url_s = self.top_url + 'ck_public_qry_cpty.cp_personcase_srch_details?backto=P&soundex_ind=&partial_ind=checked&last_name=[last_name]&first_name=&middle_name=&begin_date='+ from_date.strftime('%d-%b-%Y').lower() +'&end_date=&case_type=ALL&id_code=&PageNo=1'
        # test url
        # self.start_urls = ['https://courtconnect.courts.delaware.gov/cc/cconnect/ck_public_qry_cpty.cp_personcase_srch_details?backto=P&soundex_ind=&partial_ind=checked&last_name=a&first_name=&middle_name=&begin_date=17-sep-2022&end_date=&case_type=ALL&id_code=&PageNo=1']
        self.start_urls = [self.url_s.replace('[last_name]', letter) for letter in list(string.ascii_lowercase)]
    

    def parse(self, response):  
        self.logger.info('Parse function called on {}'.format(response.url))
        trs = response.xpath('//table[2]//tr')  
        # start from the second row         
        for tr in trs[-(len(trs) - 1):]:
            id = tr.css('td:nth-child(1)::text').get(default = "")
            party_name = tr.css('td:nth-child(2)::text').get(default = "")
            case_id = tr.css('td:nth-child(3) a::text').get(default = "")
            address = '\n'.join(tr.xpath('td[3]/text()').getall())
            case_title = ""
            i_sels = tr.xpath(".//i");
            if len(i_sels) > 0:
                i_case_sel = i_sels[len(i_sels) - 1]
                case_title = i_case_sel.xpath("text()").get(default = "")
            party_type = tr.xpath("td[4]/text()").get(default = "")
            party_end_date = tr.xpath("td[5]/text()").get(default = "")
            filing_date = tr.xpath("td[6]/text()").get(default = "")
            case_status = tr.xpath("td[7]/text()").get(default = "")

            loader = ItemLoader(item=DelawareItem())
            loader.add_value('id', id)
            loader.add_value('party_name', party_name)
            loader.add_value('case_id', case_id)
            loader.add_value('case_title', case_title)
            loader.add_value('address', address)
            loader.add_value('party_type', party_type)
            loader.add_value('party_end_date', party_end_date)
            loader.add_value('filing_date', filing_date)
            loader.add_value('case_status', case_status)
            delaware_item = loader.load_item()

            # next_page = response.urljoin(next_page)
            complete_details_link = self.top_url + 'ck_public_qry_doct.cp_dktrpt_docket_report?backto=P&case_id='+ case_id +'&begin_date=&end_date='           
            yield scrapy.Request(url = complete_details_link, callback = self.parse_case_details, errback = self.process_error, meta = {'delaware_item': delaware_item})
            
        next_url = response.xpath('//a[text()="Next->"]/@href').get()        
        if next_url is not None:
            next_url = self.top_url + next_url
            yield scrapy.Request(url = next_url, callback = self.parse, errback = self.process_error)

    def parse_case_details(self, response):
        self.logger.info('parse_case_details function called on {}'.format(response.url))
        delaware_item = response.meta['delaware_item']
        loader = ItemLoader(item = delaware_item)
        tables = response.xpath("//table")  
        # listed parties
        # it may contain none or extra few parties not listed in the search result
        extra_parties = []      
        # docket entries
        entries = []
        # party associations
        sequence_to_party_id = {}
        sequence_to_sequence = {}
        associations = {}
        for table in tables:
            th = table.xpath(".//tr[1]/th[1]/text()").get(default = '').strip()
            if th == "Seq #":
                # we have found our table 
                trs = table.xpath(".//tr[@valign='top'][not(@align)]")
                for tr in trs:    
                    # get associations                
                    seq = tr.xpath("td[1]/text()").get(default = '').strip()
                    linked_seq = tr.xpath("td[2]/text()").get(default = '').strip()
                    party_id = tr.xpath("td[5]/a/text()").get(default = '').strip()
                    if seq != "" and linked_seq != "" and party_id != "":
                        sequence_to_party_id[seq] = party_id
                        # check if we have an association between the parties already 
                        linked_seqs = [seq.strip() for seq in linked_seq.split(",")]
                        for linked_seq in linked_seqs:
                            if sequence_to_sequence.get(linked_seq) != seq:
                                sequence_to_sequence[seq] = linked_seq
                    # get parties with id
                    party_type = tr.xpath("td[4]/text()").get(default = "").strip()
                    party_name = " ".join(tr.xpath("td[6]//text()").getall()).strip()
                    next_row = tr.xpath("following-sibling::tr[1]")
                    party_address = "\n".join(next_row.xpath("td[2]/text()").getall()).strip()
                    if party_id != "":
                        extra_parties.append(dict(id = party_id, name = party_name, type = party_type, address = party_address))

                break
        # we create the party id associations based on sequence_to_sequence
        for seq in sequence_to_sequence:
            linked_seq = sequence_to_sequence[seq]            
            associations[sequence_to_party_id[seq]] = sequence_to_party_id[linked_seq]
        # last table contains docket information
        table = tables[len(tables) - 1]
        trs = table.xpath("tr[@valign='top']")
        for tr in trs:
            date_time = ' '.join(tr.xpath("td[1]/text()").getall())
            description = tr.xpath("td[2]/text()").get(default = "")
            name = tr.xpath("td[3]/text()").get(default = "")
            monetary = tr.xpath("td[4]/text()").get(default = "")
            next_row = tr.xpath("following-sibling::tr[1]")
            complete_entry = next_row.xpath("td[2]/text()").get(default = "")
            entries.append({
                "date_time": date_time.strip(),
                "description": description.strip(),
                "name": name.strip(),
                "monetary": monetary.strip(),
                "complete_entry": complete_entry.strip()
            })
        loader.add_value('associations', associations)
        loader.add_value('docket_entries', json.dumps(entries))
        loader.add_value('extra_parties', extra_parties)
        yield loader.load_item()
    
    def process_error(self, failure):
        logging.error(repr(failure))
        url = failure.request.url
        error_type = failure.type

        utils = Utils()
        utils.insert_error_log(dict(url = url, error_type = error_type, error_message = repr(failure)))

