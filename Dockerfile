FROM python:3.6
WORKDIR /app
ADD . /app
EXPOSE 80
CMD ["python", "__main__.py", "server"]
