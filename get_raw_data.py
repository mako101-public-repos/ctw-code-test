import os
import requests
from datetime import datetime
from sqlalchemy import Integer, Column, Date, Float, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dotenv import load_dotenv

load_dotenv()

# Define the AlphaVantage API parameters
try:
    api_key = os.environ['API_KEY']
except KeyError:
    raise EnvironmentError('Please set `API_KEY` environmental variable')

symbol = 'AAPL'
outputsize = 'compact'

# Retrieve daily stock data from AlphaVantage
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize={outputsize}&apikey={api_key}'
response = requests.get(url)
data = response.json()['Time Series (Daily)']

# Define the database path
database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'financial_data.db')

# Define the SQLAlchemy engine and session
engine = create_engine(f'sqlite:///{database_path}', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# Define the ORM base
Base = declarative_base()


# symbol, date, open_price, close_price, volume
# Define the Stock model
class Stock(Base):
    __tablename__ = 'financial_data'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10))
    date = Column(Date)
    open_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)

    def __repr__(self):
        return f"<Stock(symbol='{self.symbol}', date='{self.date}', close_price='{self.close_price})'>"


# Create the 'financial_data' table if it doesn't exist
Base.metadata.create_all(engine)

# Store the retrieved data in the database
for date_string, values in data.items():
    stock = Stock(
        symbol=symbol,
        date=datetime.strptime(date_string, "%Y-%m-%d"),
        open_price=float(values['1. open']),
        close_price=float(values['4. close']),
        volume=float(values['6. volume'])
    )
    session.add(stock)

session.commit()
session.close()
