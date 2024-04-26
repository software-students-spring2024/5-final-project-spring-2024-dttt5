# Use the official MongoDB image from the Docker Hub
FROM mongo:latest

# Copy the initialization script to the container
COPY init-mongo.js /docker-entrypoint-initdb.d/

# Expose the default MongoDB port
EXPOSE 27017
