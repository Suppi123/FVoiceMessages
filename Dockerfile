FROM ubuntu:24.04

RUN apt-get update && apt-get install -y python3 python3-pip ffmpeg

WORKDIR /usr/src/app

RUN pip install -U torch faster-whisper python-telegram-bot huggingface_hub[hf_xet] --break-system-packages

COPY main.py .

CMD ["python3", "main.py"]
