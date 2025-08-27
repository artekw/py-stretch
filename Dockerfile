FROM alpine:3.14
MAINTAINER Artur Wronowski "arteqw@gmail.com"
RUN apk add --no-cache python3 python3-dev py3-pip py3-setuptools build-base zlib-dev jpeg-dev tiff-dev freetype-dev libxslt-dev libxml2-dev

COPY . /app
WORKDIR /app
RUN pip3 install tornado pypdf2 pillow img2pdf
ENTRYPOINT ["python3"]
CMD ["app.py"]
