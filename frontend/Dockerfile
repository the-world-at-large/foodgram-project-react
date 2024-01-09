# build env
FROM node:13.12.0-alpine as build

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . ./

RUN npm run build

RUN mkdir -p usr/share/nginx/html/

CMD cp -r build/* /usr/share/nginx/html/
