FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN chmod 755 .

COPY . /app

CMD ["python", "main.py"]