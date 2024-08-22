# Use an official Python runtime as a parent image
FROM python:3.12.3

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first for better caching
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . /app/

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app

# Switch to non-root user
# USER appuser

# Define the command to run the application
CMD ["sh", "run.sh"]
