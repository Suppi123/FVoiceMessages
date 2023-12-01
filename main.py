import os
import whisper
import logging
import telegram.ext.filters
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackContext, MessageHandler

token = os.environ.get('TELEGRAM_TOKEN')
model_name = os.environ.get('WHISPER_MODEL')

print(os.environ)

print(token)
print(model_name)

model = whisper.load_model(model_name)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def transcript_file(file) -> list:
    # download the voice note as a file
    result = model.transcribe(file.file_path)
    segments = result['segments']
    segment_chunks = [segments[x:x + 10] for x in range(0, len(segments), 10)]
    messages = []
    for segment_list in segment_chunks:
        message = ''
        for segment in segment_list:
            message += f"{segment['text']}\n\n"
        messages.append(message)
    return messages

async def notify_user(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Wait a minute, "
                                                                          "I'll transcribe your audio file.")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="🤖 Hi, I am a bot that can transcribe voice messages. "
                                        "Just send me an audio file and I'll get started")


async def get_voice(update: Update, context: CallbackContext) -> None:
    await notify_user(update, context)
    # get basic info about the voice note file and prepare it for downloading
    file = await context.bot.get_file(update.message.audio.file_id)
    transcript = await transcript_file(file)
    for message in transcript:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


async def get_audio(update: Update, context: CallbackContext) -> None:
    await notify_user(update, context)
    # get basic info about the voice note file and prepare it for downloading
    file = await context.bot.get_file(update.message.audio.file_id)
    transcript = await transcript_file(file)
    for message in transcript:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message)


if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()

    start_handler = CommandHandler('start', start)
    voice_handler = MessageHandler(telegram.ext.filters.VOICE, get_voice)
    audio_handler = MessageHandler(telegram.ext.filters.AUDIO, get_audio)

    application.add_handler(start_handler)
    application.add_handler(voice_handler)
    application.add_handler(audio_handler)

    application.run_polling()
