FROM  node:14

WORKDIR /app

COPY data/package*.json ./

RUN npm install
RUN npm install react-router-dom

COPY data/. .

# Production
# RUN npm run build

# Run app 
CMD [ "npm", "start" ]
