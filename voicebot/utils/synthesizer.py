import pyttsx3
import os

synthesizer = pyttsx3.init()

def synthesize_text(text, output_path):
    synthesizer.save_to_file(text, output_path)
    synthesizer.runAndWait()

def delete_synthesized_audio(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
