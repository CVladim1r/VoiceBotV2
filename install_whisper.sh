#!/bin/bash

# Установить openai-whisper
pip install -U openai-whisper

# Установить whisper из репозитория GitHub
pip install git+https://github.com/openai/whisper.git

# Обновить whisper из репозитория GitHub
pip install --upgrade --no-deps --force-reinstall git+https://github.com/openai/whisper.git

pip install setuptools-rust

# Запустить whisper с моделью medium
whisper audio.flac audio.mp3 audio.wav --model medium

# Запустить whisper с моделью small
whisper audio.flac audio.mp3 audio.wav --model small
