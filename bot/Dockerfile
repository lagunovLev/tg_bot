FROM python:latest

WORKDIR /bot
ENV PYTHONPATH="${PYTHONPATH}:/bot"
RUN pip install --upgrade pip
COPY ./requirements.txt /bot/requirements.txt
RUN pip install -r requirements.txt
COPY . /bot

#ENV PORT=5000
#EXPOSE 8080
#CMD ["gunicorn", "-b", "0.0.0.0:8080", "main"]