FROM python:3.9-alpine

WORKDIR /app

COPY ./conf/requirements.txt ./conf/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r conf/requirements.txt
RUN pip install numpy

ENV DJANGO_SETTINGS_MODULE=tournament_project.settings

CMD [ "./start_tournament.sh"]
