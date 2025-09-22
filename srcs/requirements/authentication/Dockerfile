FROM python:3.9-alpine

WORKDIR /app

ENV TZ=Europe/Paris

COPY ./conf/requirements.txt conf/
RUN pip install --no-cache-dir -r conf/requirements.txt
CMD [ "./start_authentication.sh"]
