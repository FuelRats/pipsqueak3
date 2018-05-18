# Use an official Python runtime as a parent image
FROM python:3.6.5-alpine
# fetch git, as we will need it.
RUN apk add --no-cache git
# Copy the current directory contents into the container at /app
ADD . /mechasqueak

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r /mechasqueak/requirements.txt

# Set the working directory to /mechasqueak
WORKDIR /mechasqueak

# Run our tests when the container launches by default
CMD ["pytest"]