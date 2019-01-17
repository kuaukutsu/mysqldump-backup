FROM python:2-stretch

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get clean
RUN apt-get install -y \
    libxml2-dev \
    libxslt-dev \
    libcurl4-openssl-dev \
    mysql-client \
    p7zip-full \
    python-dev \
    python-pycurl \
    wget

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python"]