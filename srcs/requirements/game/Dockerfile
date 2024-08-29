FROM python:3.9

WORKDIR /app

COPY ./conf/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "src/manage.py", "runserver", "0.0.0.0:8000"]
