# Axelar Wallet Monitor

A lightweight Python service that monitors an Axelar wallet for activity and sends alerts to Telegram.

Monitors:
- Incoming/outgoing bank transfers
- Staking: delegate, undelegate, redelegate
- Any other txs involving the wallet (fallback summary)

It polls the Axelar LCD and pushes alerts via Telegram bot.

## Configuration

Environment variables:
- `AXELAR_WALLET`: Your wallet address (axelar1...)
- `TELEGRAM_BOT_TOKEN`: Telegram bot token (optional; if unset, alerts are printed to stdout)
- `TELEGRAM_CHAT_ID`: Telegram chat or user ID (required if TELEGRAM_BOT_TOKEN is set)
- `AXELAR_LCD`: LCD endpoint (default: https://lcd-axelar.imperator.co:443)
- `POLL_INTERVAL`: Seconds between polls (default: 20)
- `HEALTH_PORT`: Port for health check endpoint (default: 8080)

## Health Check

The project includes a separate health check service that exposes an endpoint at `/health` on port 8080 (configurable via `HEALTH_PORT`).

Example response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-08T12:34:56Z",
  "service": "axelar-wallet-monitor-health",
  "wallet": "axelar1...",
  "version": "1.0.0"
}
```

You can test it locally with:
```bash
curl http://localhost:8080/health
```

### Running the health service standalone

```bash
python app/health_service.py
```

## Run locally

1) Install dependencies:

```bash
pip install -r requirements.txt
```

2) Set environment variables and run:

```bash
export AXELAR_WALLET=axelar1... \
  TELEGRAM_BOT_TOKEN={{TELEGRAM_BOT_TOKEN}} \
  TELEGRAM_CHAT_ID={{TELEGRAM_CHAT_ID}} \
  POLL_INTERVAL=15

python app/main.py
```

If you don't set `TELEGRAM_BOT_TOKEN`, messages print to stdout.

## Docker

Build the main monitoring service:

```bash
docker build -t axelar-wallet-monitor .
```

Build the health service:

```bash
docker build -f Dockerfile.health -t axelar-wallet-monitor-health .
```

Run the main service with Docker:

```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  -e AXELAR_WALLET=axelar1... \
  -e TELEGRAM_BOT_TOKEN={{TELEGRAM_BOT_TOKEN}} \
  -e TELEGRAM_CHAT_ID={{TELEGRAM_CHAT_ID}} \
  -e POLL_INTERVAL=15 \
  axelar-wallet-monitor
```

Run the health service:

```bash
docker run --rm \
  -p 8080:8080 \
  -e AXELAR_WALLET=axelar1... \
  -e HEALTH_PORT=8080 \
  axelar-wallet-monitor-health
```

## Docker Compose

For easier deployment with both services, use Docker Compose:

```bash
# Set environment variables in .env file or export them
export AXELAR_WALLET=axelar1...
export TELEGRAM_BOT_TOKEN={{TELEGRAM_BOT_TOKEN}}
export TELEGRAM_CHAT_ID={{TELEGRAM_CHAT_ID}}

# Run both services with Docker Compose
docker-compose up -d
```

This will start:
- The main monitoring service (`axelar-wallet-monitor`)
- The health check service (`health`) on port 8080

Both services will automatically restart unless stopped, and the monitoring service will persist height data in the `./data` directory.

## Project Structure

```
├── app/
│   ├── main.py           # Entry point for monitoring service
│   ├── monitor.py        # Main monitoring loop
│   ├── lcd.py            # LCD API interactions
│   ├── alert.py          # Telegram bot functionality
│   ├── data.py           # Height persistence
│   ├── utils.py          # Utility functions
│   └── health_service.py # Standalone health check service
├── data/
│   └── height.txt        # Persisted block height
├── infrastructure/
│   └── google_cloud.sh   # Google Cloud deployment script
├── docker-compose.yml    # Docker Compose for both services
├── Dockerfile            # Docker build for monitoring service
├── Dockerfile.health     # Docker build for health service
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Notes

- Uses `/cosmos/tx/v1beta1/txs` LCD endpoint with an events query. Adjust the query in `build_event_clauses` if you want to narrow/broaden matches.
- Basic de-duplication by txhash. Height is persisted in `data/height.txt` for resuming after restarts.
- For production, consider running behind a process manager (Docker restart policy, systemd, k8s) and add observability.
- Transaction details are sent as Mintscan URLs for easy blockchain exploration.
- The health check service runs independently from the monitoring service for better separation of concerns.
- Health service runs on port 8080 by default (configurable via `HEALTH_PORT` environment variable).

