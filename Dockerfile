# Use the Python 3.8 base image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements_dev.in file from the host into the container
COPY requirements_dev.in .

# Install pip-tools
RUN pip install pip-tools

# Generate requirements_dev.txt
RUN pip-compile --output-file=requirements_dev.txt --resolver=backtracking requirements_dev.in

# Install the packages from requirements_dev.txt
RUN pip install -r requirements_dev.txt

# Print the contents of requirements_dev.txt
CMD cat requirements_dev.txt
