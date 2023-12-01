import os
import whisper
import logging
import telegram.ext.filters
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext, MessageHandler

# Define your environment variables or use hardcoded values
token = os.environ.get('TELEGRAM_TOKEN')
model_name = os.environ.get('WHISPER_MODEL')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load the Whisper ASR model
logging.log(logging.INFO, f'Load model {model_name}')
model = whisper.load_model(model_name)
logging.log(logging.INFO, 'Model loaded')


async def transcript_file(file) -> list:
    """
    Transcribes an audio file using the Whisper ASR model.

    Parameters:
        file (telegram.File): The audio file to be transcribed.

    Returns:
        list: A list of transcribed text segments.
    """
    # download the voice note as a file
    result = model.transcribe(file.file_path)
    segments = result['segments']
    segment_chunks = [segments[x:x + 10] for x in range(0, len(segments), 10)]
    messages = []
    for segment_list in segment_chunks:
        message = ''
        for segment in segment_list:
            message += f"{segment['text']}\n\n"
        messages.append(str.strip(message))
    return messages


async def process_message(update: Update, context: CallbackContext, file):
    """
    Processes the transcribing of an audio file asynchronously.

    Parameters:
        update (telegram.Update): The incoming update.
        context (telegram.ext.CallbackContext): The callback context.
        file (telegram.File): The audio file to be transcribed.
    """
    transcript = await transcript_file(file)
    for message in transcript:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def notify_user(update: Update, context: CallbackContext):
    """
    Notifies the user about the ongoing transcription process.

    Parameters:
        update (telegram.Update): The incoming update.
        context (telegram.ext.CallbackContext): The callback context.
    """
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'll transcribe your audio file. "
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
    await process_message(update, context, file)


async def get_audio(update: Update, context: CallbackContext) -> None:
    """
    Handles incoming audio messages for transcription.

    Parameters:
        update (telegram.Update): The incoming update.
        context (telegram.ext.CallbackContext): The callback context.
    """
    await notify_user(update, context)
    file = await context.bot.get_file(update.message.audio.file_id)
    await process_message(update, context, file)

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
