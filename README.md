# Delaware Court Case ETL tool  
This tool can be used to extract records from Delaware Court Website.  
https://courtconnect.courts.delaware.gov  

## How to run  
Clone the project 
```
git clone https://github.com/sunaram/delaware-cases-etl
cd delaware-cases-etl 
```
### 1. Using docker  
Make sure you have docker installed and running in your system.  
``` 
docker compose build  
```
You are ready to run the scraper  
Get a csv dump of the scraped data  
```
docker compose run python scrapy crawl delaware -o /data/delaware.csv
```
You will see the delaware.csv file in the "data" directory 
Scrape cases with filing date from 2 days to now 
```
docker compose run python scrapy crawl delaware -a days=2 -o /data/delaware.csv
```
Save the data to a sqlite db  
```
docker compose run -e CONNECTION_STRING=sqlite:////data/delaware.db python scrapy crawl delaware
```
You can also store the data in mysql database by passing connection string acceptable in a SQLAlchemy format  

### 2. Using Python Environment  
You need to have Python3.9+ and venv installed in your system  
#### Windows CMD
```
python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
#### Bash
```
python3 -m venv ./venv
./venv/bin/activate
```
Now you are ready to crawl the case data from the court website  

Get a csv dump of the scraped data  
```
scrapy crawl delaware -o data/delaware.csv
```
You will see the delaware.csv file in the "data" directory 
Scrape cases with filing date from 2 days to now 
```
scrapy crawl delaware -a days=2 -o data/delaware.csv
```
Save the data to a sqlite db  
```
scrapy crawl delaware
```
You can also store the data in mysql database by passing connection string acceptable in a SQLAlchemy format 