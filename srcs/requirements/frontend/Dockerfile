FROM  node:14-alpine

WORKDIR /app

COPY data/package*.json ./

RUN npm install

COPY data/. .

# Production
# RUN npm run build

# Run app 
CMD [ "npm", "start" ]

RUN npm install react-bootstrap bootstrap
RUN npm install react-router-dom
RUN npm install axios
