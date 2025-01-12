# Set base image (host OS)
FROM python:latest

# Copy the content of the project directory to the working directory
COPY . /app

# Set the working directory in the container
WORKDIR /app

# Install any dependencies
RUN pip install -r requirements.txt

# Specify the Flask environment port
ENV PORT=5000

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "main"]