FROM python:3.9-alpine

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Python script to generate data

COPY financial/ /app/financial/
COPY model.py /app/model.py

## TEMP TEST
#COPY financial_data.db /app/financial_data.db

# Expose Application port
EXPOSE 5000

WORKDIR /app/financial/

# Start the application
CMD ["python3", "run.py"]
