FROM  node:14-alpine

WORKDIR /app

COPY data/package*.json ./

RUN apk add --no-cache tzdata
ENV TZ=Europe/Paris

RUN npm install
RUN npm install qrcode.react

COPY data/. .

# Production
# RUN npm run build

# Run app 
CMD [ "npm", "start" ]

RUN npm install react-bootstrap bootstrap
RUN npm install react-router-dom
RUN npm install axios
RUN npm install reconnecting-websocket

