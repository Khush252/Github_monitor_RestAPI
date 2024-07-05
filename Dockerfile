FROM python:3.11-slim

WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on (if applicable)
# EXPOSE 8000

# Set environment variables (if necessary)
# ENV VARIABLE_NAME=value

# Run the main script when the container launches
CMD ["python3", "main.py"]
