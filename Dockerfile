FROM ubuntu:22.04

RUN apt update && \ 
    apt install python3.11 python3-pip binutils libproj-dev gdal-bin -y && \
    pip install --upgrade pip

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .