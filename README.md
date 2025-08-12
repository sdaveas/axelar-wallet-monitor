# Axelar Wallet Monitor

A lightweight Python service that monitors an Axelar wallet for## Docker Compose

For easier deployment, use Docker Comp## Notes

- Uses `/cosmos/tx/v1beta1/txs` LCD endpoint with an events query. Adjust the query in `build_event_clauses` if you want to narrow/broaden matches.
- Basic de-duplication by txhash. Height is persisted in `data/height.txt` for resuming after restarts.
- For production, consider running behind a process manager (Docker restart policy, systemd, k8s) and add observability.
- Transaction details are sent as Mintscan URLs for easy blockchain exploration.
- The health check service runs in a separate thread within the main application process.
- Health service runs on port 8080 by default (configurable via `HEALTH_PORT` environment variable).
- Support for both minimum (`tx.height>=`) and maximum (`tx.height<=`) height filtering in LCD queries.`bash
# Set environment variables in .env file or export them
export AXELAR_WALLET=axelar1...
export TELEGRAM_BOT_TOKEN={{TELEGRAM_BOT_TOKEN}}
export TELEGRAM_CHAT_ID={{TELEGRAM_CHAT_ID}}
export HEALTH_PORT=8080

# Run with Docker Compose
docker-compose up -d
```

This will start the service with both monitoring and health check functionality. The health endpoint will be available on the configured port (default 8080), and the service will persist height data in the `./data` directory. alerts to Telegram.

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

The service includes an integrated health check endpoint at `/health` on port 8080 (configurable via `HEALTH_PORT`).

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

The health check service runs in a separate thread alongside the main monitoring service.

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

Build the image (includes both monitoring and health services):

```bash
docker build -t axelar-wallet-monitor .
```

Run with Docker:

```bash
docker run --rm 
  -p 8080:8080 
  -v $(pwd)/data:/app/data 
  -e AXELAR_WALLET=axelar1... 
  -e TELEGRAM_BOT_TOKEN={{TELEGRAM_BOT_TOKEN}} 
  -e TELEGRAM_CHAT_ID={{TELEGRAM_CHAT_ID}} 
  -e POLL_INTERVAL=15 
  -e HEALTH_PORT=8080 
  axelar-wallet-monitor
```

This runs both the monitoring service and health check endpoint in the same container.

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
│   ├── main.py           # Entry point - starts both monitoring and health services
│   ├── monitor.py        # Main monitoring loop
│   ├── health.py         # Integrated health check service
│   ├── lcd.py            # LCD API interactions
│   ├── alert.py          # Telegram bot functionality
│   ├── data.py           # Height persistence
│   ├── utils.py          # Utility functions
│   └── logger.py         # Logging configuration
├── data/
│   └── height.txt        # Persisted block height
├── infrastructure/
│   └── google_cloud.sh   # Google Cloud deployment script
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Docker build configuration
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

