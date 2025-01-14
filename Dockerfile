FROM python:latest

WORKDIR /app
RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app

#ENV PORT=5000
#EXPOSE 8080
#CMD ["gunicorn", "-b", "0.0.0.0:8080", "main"]