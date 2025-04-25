# Speech2Text Telegram Bot

Tired of listening to voice messages? This bot is the solution. Send this bot your voice messages and it will send you back the transcript.

## Installation instructions

Docker must be installed on the system on which you want to run the program: https://docs.docker.com/engine/install/

Create a Telegram Bot. For this you need the Telegram BotFather: https://telegram.me/BotFather

Add your Telegram token in the docker-compose.yml after the environment variable TELEGRAM_TOKEN

You can also set different AI models to perform the transcription. You can find out more here: https://github.com/openai/whisper#available-models-and-languages

## Start the bot

You can start the bot with 
```bash
docker compose up -d
```
