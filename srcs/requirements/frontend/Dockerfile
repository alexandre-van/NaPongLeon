FROM  node:14

# For development
RUN apt install git neovim
RUN git clone https://github.com/NvChad/NvChad ~/.config/nvim --depth 1

WORKDIR /app

# Install create-react-app
#RUN npm install -g create-react-app

# Create new React app
#RUN create-react-app .

#COPY ./data/* .
COPY data/package*.json ./

RUN npm install

#EXPOSE 3000
COPY data/. .

# Run app
CMD [ "npm", "start" ]
