FROM python:3.11-slim


# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install ngrok (no authentication needed)
RUN curl -O https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip && \
    unzip ngrok-stable-linux-amd64.zip && \
    rm ngrok-stable-linux-amd64.zip && \
    mv ngrok /usr/local/bin/

# Set up application
WORKDIR /app
COPY . .
# COPY .env .env  # Ensure this line explicitly copies the .env
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]