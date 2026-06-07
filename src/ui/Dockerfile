FROM node:20

WORKDIR /app

COPY package*.json ./
RUN npm install

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]