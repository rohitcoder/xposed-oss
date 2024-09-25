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

#RUN pip3 install pyarmor

COPY . /app/

# Create the /tmp/xposed/ directory
RUN mkdir -p /tmp/xposed/

# Copy required files to the /tmp/xposed/ directory
RUN cp requirements.txt /tmp/xposed/
RUN cp setup.cfg /tmp/xposed/
RUN cp setup.py /tmp/xposed/

# Install the Python package (assuming it contains a setup.py file)
RUN pip3 install /tmp/xposed/

# Run xposed from python3 main.py
ENTRYPOINT ["xposed_oss"]
