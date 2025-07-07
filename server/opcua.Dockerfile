FROM python:3.10-slim

WORKDIR /server

RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY __init__.py .

EXPOSE 4840

CMD ["python", "__init__.py"]