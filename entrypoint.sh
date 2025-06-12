#!/bin/bash

# Phase 1: Start ngrok
echo "🚀 Starting ngrok on port 5050..."
ngrok http 5050 --log=stdout > /dev/null &
sleep 5  # Give ngrok time to initialize

# Phase 2: Get ngrok public URL
NGROK_URL=""
RETRIES=10
while [ -z "$NGROK_URL" ] && [ $RETRIES -gt 0 ]; do
  sleep 1
  NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[]?.public_url' | grep https)
  RETRIES=$((RETRIES-1))
done


# Phase 3: Update only the DOMAIN line in .env
echo "🔧 Setting DOMAIN=$NGROK_DOMAIN in .env"
if grep -q "^DOMAIN=" .env; then
    sed -i "s|^DOMAIN=.*|DOMAIN=\"$NGROK_DOMAIN\"|" .env
else
    echo "DOMAIN=\"$NGROK_DOMAIN\"" >> .env
fi

# Phase 4: Run FastAPI app on port 8080
echo "💻 Starting FastAPI on port 8080..."
echo "🌐 Public URL: $NGROK_URL"
echo "🔗 Local URL: http://localhost:8080"
exec uvicorn main:app --host 0.0.0.0 --port 8080
