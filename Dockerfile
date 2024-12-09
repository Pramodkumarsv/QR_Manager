# Use official Python 3.7 image as base
FROM python:3.7

# Set the working directory inside the container
WORKDIR /app

# Copy the entire application code into the container's working directory
ADD . .

# Install the dependencies from requirements.txt
RUN pip install -r requirements.txt

# Expose the application port
EXPOSE 5000

# Command to run the application (if applicable)
CMD ["python", "app.py"]
