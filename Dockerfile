FROM python:3.9-alpine

RUN pip install --upgrade pip
COPY requirements-docker.txt .
RUN pip install -r requirements-docker.txt

# Copy the Python script to generate data
COPY financial/ /app/financial/
COPY model.py /app/model.py

# Read MYSQL password from the environment
ENV MYSQL_PWD=${MYSQL_PWD}
# Expose Application port
EXPOSE 5000

WORKDIR /app/financial/

# Start the application
CMD ["python3", "run.py"]
