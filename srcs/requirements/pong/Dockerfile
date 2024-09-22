FROM python:3.9

WORKDIR /app

COPY ./conf/requirements.txt ./conf/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r conf/requirements.txt
RUN pip install numpy

CMD [ "./conf/start_pong.sh"]
