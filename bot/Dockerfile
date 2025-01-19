FROM python:latest

WORKDIR /bot
RUN pip install --upgrade pip
COPY ./requirements.txt /bot/requirements.txt
RUN pip install -r requirements.txt
COPY . /bot
ENV PYTHONPATH /bot
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

CMD ["python", "__init__.py"]

#ENV PORT=5000
#EXPOSE 8080
#CMD ["gunicorn", "-b", "0.0.0.0:8080", "main"]