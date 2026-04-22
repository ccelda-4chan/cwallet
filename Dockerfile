# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the port (Render provides this via the $PORT env var)
ENV PORT 8000

# Start the application using uvicorn
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
