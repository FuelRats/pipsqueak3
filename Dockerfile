# Use an official Python runtime as a parent image
FROM python:3.6.5-stretch


# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r /app/requirements.txt

# Make port 80 available to the world outside this container
#EXPOSE 80

# Set the working directory to /app
WORKDIR /app

# Run our tests when the container launches by default
CMD ["pytest"]