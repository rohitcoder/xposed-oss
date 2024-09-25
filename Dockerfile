# Use the official Python image as the base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the local requirements.txt file to the container at /app
COPY requirements.txt /app/

RUN pip install --upgrade certifi

# Install the dependencies from requirements.txt
RUN pip3 install -r requirements.txt --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org

# Install gcloud cli
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && apt-get update -y && apt-get install google-cloud-sdk -y

## Check if gcloud is installed
RUN gcloud --version

# Copy the entire app to the working directory
COPY . /app/

# Create the /tmp/xposed/ directory
RUN mkdir -p /tmp/xposed/

# Copy required files to the /tmp/xposed/ directory
RUN cp requirements.txt /tmp/xposed/
RUN cp setup.cfg /tmp/xposed/
RUN cp setup.py /tmp/xposed/

# Install the Python package (assuming it contains a setup.py file)
RUN pip3 install /tmp/xposed/

# Install NGINX
RUN apt-get update && apt-get install -y nginx

# Remove the default NGINX configuration file
RUN rm /etc/nginx/sites-enabled/default

# Create a new NGINX configuration file
RUN echo "server { \
    listen 80; \
    server_name localhost; \
    root /app/results; \
    index index.html; \
    location / { \
        try_files \$uri \$uri/ =404; \
    } \
}" > /etc/nginx/sites-available/default

# Link the configuration file
RUN ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/

# Expose port 80 to access NGINX
EXPOSE 80

# Run NGINX and your Python application together
CMD service nginx start && python3 main.py
