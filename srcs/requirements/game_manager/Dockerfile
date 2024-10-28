FROM python:3.9-alpine

WORKDIR /app

COPY ./conf/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ENV DJANGO_SETTINGS_MODULE=project.settings

CMD ["./start_game_manager.sh"]
