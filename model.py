from sqlalchemy.orm import declarative_base
from sqlalchemy import Integer, Column, Date, Float, String


# Define the ORM base
Base = declarative_base()


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
