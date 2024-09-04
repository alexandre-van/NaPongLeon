FROM python:3.9

WORKDIR /app

COPY ./conf/requirements.txt ./conf/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r conf/requirements.txt

CMD [ "python", "src/manage.py", "runserver", "0.0.0.0:8000"]
