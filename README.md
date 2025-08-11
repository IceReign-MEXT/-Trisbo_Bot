# Trisbo Bot

## Overview
Trisbo Bot is a Telegram bot that tracks your Solana and Ethereum wallets, checks balances, and manages paid subscriptions for different service durations. It is designed to integrate with smart contracts for automated funds sweeping in the future.

## Features
- Check wallet balances (SOL & ETH)
- Subscribe to plans (3h, 6h, 12h, 24h) with different prices
- Subscription management
- Planned smart contract integration for secure fund sweeping
- Secure and private configuration

## How to use
1. Clone this repo.
2. Fill in `config.json` with your details and API keys.
3. Run `pip install -r requirements.txt`
4. Run the bot: `python main.py`
5. Use Telegram commands `/start`, `/check`, `/subscribe <plan>`, `/status`, `/help`.

## Roadmap
- Integrate real payment verification
- Full smart contract interaction for automatic fund management
- Add more chains and wallet types
- Deploy on cloud VPS for 24/7 uptime
- User dashboard and analytics

## License
MIT License