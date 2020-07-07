# FROM python:latest
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
# FROM continuumio/miniconda3:latest

# FROM python:3.8
ARG app_location='/usr/src/app'
WORKDIR ${app_location}
# ADD requirements.txt /server/
# ADD api.py /server/
# ADD encodedecodeimg.py /server/
ADD ./ /${app_location}

RUN pip install -r requirements.txt
RUN pip install --no-cache-dir fastapi
# COPY ./app /app

EXPOSE 8080
CMD [ "uvicorn", "api:app", "--reload",  "--host", "0.0.0.0", "--port", "8080" ]

# ADD . /server
# CMD uvicorn api:app --host 127.0.0.1 --port 8000 --reload






# WORKDIR /server/
# COPY ./api.py /api.py
# # EXPOSE 8000
