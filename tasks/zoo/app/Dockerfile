FROM golang:1.22-bullseye as build

WORKDIR /build
COPY ./go.mod ./go.mod
COPY ./go.sum ./go.sum

RUN go mod download

COPY . .
RUN go build -o zoo .

FROM debian:bullseye-slim

COPY --from=build /build/zoo /app/zoo
COPY --from=build /build/templates /app/templates
COPY --from=build /build/static /app/static

WORKDIR /app
CMD ["/app/zoo"]
