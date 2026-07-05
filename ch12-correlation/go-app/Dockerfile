FROM golang:1.24-alpine AS build
WORKDIR /src
COPY go.mod .
COPY main.go .
# 直接依存だけ書いた go.mod から、間接依存と go.sum を解決する。
RUN go mod tidy
RUN CGO_ENABLED=0 go build -o /go-dice .

FROM alpine:3.21
COPY --from=build /go-dice /go-dice
EXPOSE 8001
CMD ["/go-dice"]
