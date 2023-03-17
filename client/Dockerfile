FROM node:lts-alpine as build-step

WORKDIR /app
COPY package.json  ./
COPY ./src ./src
COPY ./config ./config
COPY ./.eslintrc.js ./.eslintrc.js
COPY ./tsconfig.json ./tsconfig.json
RUN npm install
RUN npm run build

FROM caddy:alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY --from=build-step /app/dist /srv