# Use the official Python image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required for PyAudio
RUN apt-get update && apt-get install -y \
    gcc \
    libportaudio2 \
    portaudio19-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Set the default command to run the application
CMD ["python", "gui_realtime_translation.py"]
