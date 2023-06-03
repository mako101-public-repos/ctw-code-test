from datetime import datetime


def validate_date(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d").date()
        return date_string
    except:
        raise ValueError(f'Date {date_string} does not match excepted format: YYYY-MM-DD')


def validate_symbol(symbol_string):
    if (not symbol_string.isalpha()) or len(symbol_string) > 10:
        raise ValueError(f'{symbol_string} is not a valid symbol (should be a short string containing only letters)')

    return symbol_string.upper()

