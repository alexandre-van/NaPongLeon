FROM python:3.9-alpine

WORKDIR /app

COPY conf/requirements.txt .

# install django to create the project
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add --no-cache bash

CMD ["/bin/bash"]