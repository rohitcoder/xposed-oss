# Use the official Python image as the base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the local requirements.txt file to the container at /app
COPY requirements.txt /app/

# Install the dependencies from requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install gcloud CLI (if required by your application)
RUN apt-get update -y && \
    apt-get install -y curl gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    apt-get update -y && \
    apt-get install -y google-cloud-sdk

# Copy the entire app to the working directory
COPY . /app/

# Install the Python package (assuming it contains a setup.py file)
RUN pip install .

# Expose port 80 to access the Flask app
EXPOSE 80

# Command to run the application
CMD ["python3", "main.py", "--config=/app/config.yaml", "--server"]
