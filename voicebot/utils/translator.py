from deep_translator import GoogleTranslator

def translate_text(audio_file_path, target_language):
    try:
        # Read audio file content
        with open(audio_file_path, 'rb') as audio_file:
            audio_content = audio_file.read()
        
        # Translate audio content
        translator = GoogleTranslator(source='auto', target=target_language)
        translated_text = translator.translate(audio_content)
        return translated_text

    except Exception as e:
        print(f"Error translating voice message: {e}")
        return None
