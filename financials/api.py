import sys
from importlib import util
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from fastapi import FastAPI, HTTPException
from fastapi_utils.inferring_router import InferringRouter
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from validators import validate_date, validate_symbol

# Import Stock object definition
spec = util.spec_from_file_location('model', '../model.py')
module = util.module_from_spec(spec)
sys.modules['model'] = module
spec.loader.exec_module(module)
from model import Base, Stock

# FastAPI app and router
app = FastAPI()
router = InferringRouter(prefix='/api')


# Create SQLite database (assuming you've already created it)
engine = create_engine('sqlite:///../financial_data.db')
Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()


# Route to retrieve stock records with customizable dates, limits, and pagination
@router.get("/financial_data")
def get_stock_records(symbol: str, start_date: str, end_date: str,  limit: int = 5, page: int = 1):
    try:
        symbol = validate_symbol(symbol)
        query = session.query(Stock).filter(
            Stock.symbol == symbol,
            Stock.date >= validate_date(start_date),
            Stock.date <= validate_date(end_date)
        ).order_by(Stock.date.asc())

        total_records = query.count()
        total_pages = int(total_records // limit + (1 if total_records % limit > 0 else 0))

        records = query.limit(limit).offset((page - 1) * limit).all()

        if not records:
            return {
                "data": [],
                "pagination": {},
                "info": {'error': f'No records found for symbol {symbol}'}
            }

        return {
            "data": [record.__dict__ for record in records],
            "pagination": {
                "count": total_records,
                "page": page,
                "limit": limit,
                "pages": total_pages
            },
            "info": {'error': ''}
        }
    except Exception as e:
        return {
            "data": [],
            "pagination": {},
            "info": {'error': str(e)}
        }


# Route to perform basic statistical analysis on the stock records
@router.get("/statistics/")
def get_stock_records_statistics(symbol: str, start_date: str, end_date: str):
    try:
        symbol = validate_symbol(symbol)
        query = session.query(
            func.avg(Stock.open_price).label('average_daily_open_price'),
            func.avg(Stock.close_price).label('average_daily_close_price'),
            func.avg(Stock.volume).label('average_daily_volume'),
        ).filter(
            Stock.symbol == symbol,
            Stock.date >= start_date,
            Stock.date <= end_date
        )

        result = query.first()
        if result == (None, None, None):
            return {
                "data": [],
                "info": {'error': f'No records found for symbol {symbol}'}
            }

        return {
            "data": {
                "start_date": start_date,
                "end_date": end_date,
                "symbol": symbol,
                "average_daily_open_price": float(f'{result.average_daily_open_price:.2f}'),
                "average_daily_close_price": float(f'{result.average_daily_close_price:.2f}'),
                "average_daily_volume": int(result.average_daily_volume)
            },
            "info": {'error': ''}
        }
    except Exception as e:
        return {
            "data": [],
            "info": {'error': str(e)}
        }


app.include_router(router)

# Endpoint to list available API endpoints
@app.get("/api")
def get_root():
    routes = []
    for route in app.routes:
        if isinstance(route, FastAPI) or route.path == "/":
            continue
        routes.append({"path": route.path, "methods": route.methods})
    return routes


# Swagger UI Endpoint
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")


# OpenAPI Schema endpoint
@app.get("/openapi.json", include_in_schema=False)
def get_open_api_endpoint():
    return get_openapi(title="API Docs", version="1.0.0", routes=app.routes)
