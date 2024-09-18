FROM python:3.9

WORKDIR /app

COPY ./conf/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#COPY src .
#RUN python manage.py makemigrations
#RUN python manage.py migrate


CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000"]
