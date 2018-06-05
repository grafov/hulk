FROM golang:1-alpine

RUN apk add --no-cache git \
  && go get -d -v github.com/grafov/hulk \
  && go install github.com/grafov/hulk \
  && rm -rf ~/go/src/github.com/grafov/hulk \
  && apk del git

ENTRYPOINT ["hulk"]

CMD ["--help"]
