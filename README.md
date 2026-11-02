name: Videografiya yangiliklari

on:
  schedule:
    - cron: "0 3 * * *"
  workflow_dispatch:

jobs:
  send-news:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install feedparser requests
      - run: python news_agent.py
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
