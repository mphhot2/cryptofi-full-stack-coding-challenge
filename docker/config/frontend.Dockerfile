FROM node:16-alpine

WORKDIR /app

COPY /frontend ./frontend
COPY /docker ./docker

RUN cd ./frontend
RUN yarn install

CMD ["sh", "./docker/scripts/frontend-entrypoint.sh"]