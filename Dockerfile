FROM alpine:latest AS build-image

RUN apk add --no-cache \
    python3 \
    py-pip \
    openssl \
    ca-certificates \
    python3-dev \
    build-base \
    wget

WORKDIR /app

COPY requirements.txt /app/
RUN python3 -m venv /app
RUN /app/bin/pip install -r requirements.txt

FROM alpine AS runtime-image
RUN apk add --no-cache python3 openssl ca-certificates

WORKDIR /app
COPY . /app

COPY --from=build-image /app/ ./

CMD ["/app/bin/python", "main.py"]