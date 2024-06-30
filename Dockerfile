FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0
RUN mkdir -p /app/AppFile/static/UploadFiles && chmod -R 766 /app/AppFile/static/UploadFiles \
    mkdir -p /app/AppFile/static/FirstFrame && chmod -R 766 /app/AppFile/static/FirstFrame \
    mkdir -p /app/AppFile/static/scatters && chmod -R 766 /app/AppFile/static/scatters \ 
    mkdir -p /app/AppFile/static/graphs && chmod -R 766 /app/AppFile/static/graphs \ 
    mkdir -p /app/AppFile/static/csv && chmod -R 766 /app/AppFile/static/csv

COPY . .

CMD [ "gunicorn", "--bind=0.0.0.0:8000", "--timeout", "600", "server:app" ]