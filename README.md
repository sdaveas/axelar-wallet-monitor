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

Build the image:

```bash
docker build -t axelar-wallet-monitor .
```

Run with Docker:

```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  -e AXELAR_WALLET=axelar1... \
  -e TELEGRAM_BOT_TOKEN={{TELEGRAM_BOT_TOKEN}} \
  -e TELEGRAM_CHAT_ID={{TELEGRAM_CHAT_ID}} \
  -e POLL_INTERVAL=15 \
  axelar-wallet-monitor
```

## Docker Compose

For easier deployment, use Docker Compose:

```bash
# Set environment variables in .env file or export them
export AXELAR_WALLET=axelar1...
export TELEGRAM_BOT_TOKEN={{TELEGRAM_BOT_TOKEN}}
export TELEGRAM_CHAT_ID={{TELEGRAM_CHAT_ID}}

# Run with Docker Compose
docker-compose up -d
```

The service will automatically restart unless stopped and persist height data in the `./data` directory.

## Project Structure

```
├── app/
│   ├── main.py         # Entry point
│   ├── monitor.py      # Main monitoring loop
│   ├── lcd.py          # LCD API interactions
│   ├── alert.py        # Telegram bot functionality
│   ├── data.py         # Height persistence
│   └── utils.py        # Utility functions
├── data/
│   └── height.txt      # Persisted block height
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile          # Docker build configuration
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Notes

- Uses `/cosmos/tx/v1beta1/txs` LCD endpoint with an events query. Adjust the query in `build_event_clauses` if you want to narrow/broaden matches.
- Basic de-duplication by txhash. Height is persisted in `data/height.txt` for resuming after restarts.
- For production, consider running behind a process manager (Docker restart policy, systemd, k8s) and add observability.
- Transaction details are sent as Mintscan URLs for easy blockchain exploration.

