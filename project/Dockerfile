# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    firefox-esr \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install geckodriver
RUN curl -sL https://github.com/mozilla/geckodriver/releases/download/v0.32.2/geckodriver-v0.32.2-linux64.tar.gz | tar xz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver

# Copy the current directory contents into the container
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose port 5000 for the Flask app
EXPOSE 5000

# Define the environment variable for Flask
ENV FLASK_APP interface/app.py

# Run Flask when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
