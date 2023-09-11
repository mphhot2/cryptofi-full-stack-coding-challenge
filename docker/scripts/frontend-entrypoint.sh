#!/bin/sh

cd /app/frontend
yarn start

exec "$@"