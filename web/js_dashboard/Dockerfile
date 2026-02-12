FROM node:18-alpine as build

WORKDIR /app

COPY web/js_dashboard/ /app

RUN npm install
EXPOSE 5173

CMD ["npm", "run", "dev","--","--host"]
