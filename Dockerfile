
FROM python:3.11

# Set the working directory in the container
WORKDIR /teddox

# Copy package.json and package-lock.json to the working directory
COPY requirements.txt ./

# Install application dependencies
RUN pip install -r requirements.txt

# Copy the application source code to the working directory
COPY . .

# Expose the port on which the application will run
EXPOSE 8080

# Define the command to run the application
CMD [ "python", "app.py" ]
