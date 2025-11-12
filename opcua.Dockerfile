FROM python:3.10-slim

WORKDIR /server

RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY server/ .
RUN pip install --no-cache-dir -r ./opcua_manufacturing_server/requirements.txt


EXPOSE 4840

CMD ["python", "opcua_manufacturing_server/main.py"]