"""
Telegram Transcription Bot

This script defines a Telegram bot that transcribes voice messages
using the Whisper ASR (Automatic Speech Recognition) model.
Users can send audio messages to the bot, and it will transcribe
the messages and send back the transcriptions.

Dependencies:
- python-telegram-bot
- whisper

Author: [Fabian Kopf]

References:
- Python-telegram-bot library: https://python-telegram-bot.readthedocs.io/
- Whisper library: [https://github.com/openai/whisper]
"""
import os
import logging
import torch
import telegram.ext.filters
from faster_whisper import WhisperModel
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, \
    CallbackContext, MessageHandler

# Define your environment variables or use hardcoded values
token = os.environ.get('TELEGRAM_TOKEN')
model_name = os.environ.get('WHISPER_MODEL')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
logging.info('Use device: %s', device)
compute_type = 'float16' if torch.cuda.is_available() else 'int8'
logging.info('Use compute type: %s', compute_type)

# Load the Whisper ASR model
logging.info('Load model %s', model_name)
MODEL = WhisperModel(model_name, device=device, compute_type=compute_type)
logging.log(logging.INFO, 'Model loaded')


async def transcript_file(update: Update, context: CallbackContext, file) -> list:
    """
    Transcribes an audio file using the Whisper ASR model.

    Parameters:
        file (telegram.File): The audio file to be transcribed.

    Returns:
        list: A list of transcribed text segments.
        :param file:
        :param context:
        :param update:
    """
    # download the voice note as a file and transcribe
    segments, info = MODEL.transcribe(file.file_path, beam_size=5)

    probability = round(info.language_probability * 100)
    language_guess = f"I am {probability}% sure that the language used is {info.language}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=language_guess, parse_mode='html')

    for segment in segments:
        message = "<b>[%.2fs -> %.2fs]</b>\n\n%s" % (segment.start, segment.end, str.strip(segment.text))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode='html')
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)


async def notify_user(update: Update, context: CallbackContext):
    """
    Notifies the user about the ongoing transcription process.

    Parameters:
        update (telegram.Update): The incoming update.
        context (telegram.ext.CallbackContext): The callback context.
    """
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="I'll transcribe your audio file. "
                                        "This may take a while. Stay tuned!")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Responds to the /start command with a welcome message.

    Parameters:
        update (telegram.Update): The incoming update.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context.
    """
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="🤖 Hi, I am a bot that can transcribe voice messages. "
                                        "Just send me an audio file, and I'll get started")


async def get_voice(update: Update, context: CallbackContext) -> None:
    """
    Handles incoming voice messages for transcription.

    Parameters:
        update (telegram.Update): The incoming update.
        context (telegram.ext.CallbackContext): The callback context.
    """
    await notify_user(update, context)
    file = await context.bot.get_file(update.message.voice.file_id)
    await transcript_file(update, context, file)


async def get_audio(update: Update, context: CallbackContext) -> None:
    """
    Handles incoming audio messages for transcription.

    Parameters:
        update (telegram.Update): The incoming update.
        context (telegram.ext.CallbackContext): The callback context.
    """
    await notify_user(update, context)
    file = await context.bot.get_file(update.message.audio.file_id)
    await transcript_file(update, context, file)

if __name__ == '__main__':
    # Build the Telegram bot application
    application = ApplicationBuilder().token(token).build()

    # Define command and message handlers
    start_handler = CommandHandler('start', start)
    voice_handler = MessageHandler(telegram.ext.filters.VOICE, get_voice)
    audio_handler = MessageHandler(telegram.ext.filters.AUDIO, get_audio)

    # Add handlers to the application
    application.add_handler(start_handler)
    application.add_handler(voice_handler)
    application.add_handler(audio_handler)

    # Run the bot with polling
    application.run_polling()
