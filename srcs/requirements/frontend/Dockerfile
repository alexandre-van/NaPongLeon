FROM  node:14

WORKDIR /app

# Install create-react-app
RUN npm install -g create-react-app

# Create new React app
RUN create-react-app .

#EXPOSE 3000

# Run app
CMD [ "npm", "start" ]
