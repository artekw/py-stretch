FROM alpine:3.14
MAINTAINER Artur Wronowski "arteqw@gmail.com"
RUN apk add --no-cache python3 python3-dev py3-tornado py3-pypdf2 py3-pillow py3-img2pdf jpeg-dev tiff-dev freetype-dev
COPY . /app
WORKDIR /app
ENTRYPOINT ["python3"]
CMD ["app.py"]
