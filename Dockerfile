FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

COPY . .

CMD [ "gunicorn", "--bind=0.0.0.0:8000", "--timeout", "600", "server:app" ]