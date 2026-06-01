FROM node:20-alpine AS build

WORKDIR /app
COPY frontend-realtime/package.json ./
RUN npm install

COPY frontend-realtime/ .

ARG VITE_API_URL=http://localhost:8000
ARG VITE_WS_URL=ws://localhost:8001/realtime
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL

RUN npx vite build

FROM nginx:alpine
COPY frontend-realtime/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
