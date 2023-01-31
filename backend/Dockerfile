# syntax=docker/dockerfile:1
FROM python:3 as development
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app/backend/
COPY requirements.txt /app/backend/
RUN pip install -r requirements.txt
COPY . /app/backend/