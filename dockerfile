# Use slim Python base (lighter and faster)
FROM python:3.11-slim

# Install system dependencies (same as apt.txt)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libportaudio2 \
    libopus0 \
    libvpx7 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy files into container
COPY requirements.txt .
COPY app.py .
COPY apt.txt .
COPY Procfile .
COPY runtime.txt .
COPY README.md .

# Upgrade pip and install Python packages
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose default Streamlit port
EXPOSE 8501

# Run Streamlit, binding to Railway's dynamic $PORT
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
