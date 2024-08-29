FROM python:3.9

WORKDIR /app
#RUN python3.9 -m venv .env
#RUN	source .env/bin/activate
#RUN	pip install --upgrade pip

COPY ./conf/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "src/manage.py", "runserver", "0.0.0.0:8000"]
