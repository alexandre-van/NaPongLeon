FROM python:3.9-alpine

WORKDIR /app

COPY ./conf/requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install websocket-client

COPY . /app

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000"]