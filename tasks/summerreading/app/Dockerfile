FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json .
RUN npm ci
COPY next.config.ts tsconfig.json src .
RUN npm run build

FROM imachug/kyzylborda_lib
RUN pip install gunicorn flask
WORKDIR /app
COPY --from=builder /app/out /out
CMD ["gunicorn", "-b", "unix:/tmp/app.sock", "server:app"]
