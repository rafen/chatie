import os
import tempfile

import openai
from django.http import JsonResponse
from django.shortcuts import render
from django.template.defaultfilters import linebreaksbr
from pydub import AudioSegment

openai.api_key = os.getenv("OPENAI_API_KEY")

def home(request):
    return render(request, 'home.html')

def convert_audio_format(audio_file, target_format):
    # Load audio using pydub
    audio = AudioSegment.from_file(audio_file)

    # Convert audio to the target format
    converted_audio = audio.export(format=target_format)

    return converted_audio


def transcribe_audio(audio_path):
    # Read the audio file
    with open(audio_path, 'rb') as file:
        # Perform transcription using OpenAI's Audio API
        response = openai.Audio.transcribe("whisper-1", file)

    # Get the transcript from the API response
    transcript = response['text']

    return transcript

def get_answer(transcript):
    prompt = '''Podrias darme unicamente los siguientes campos en formato JSON valido: nombre (first_name), apellido (last_name), edad (age). Tienes que ignorar cualquier otro dato. Si no encuetras el campo debes devolverlo con valores null

Ejemplo: Crear paciente Marcos Perez de 25 años de edas.
Resultado: {"first_name": "Marcos", "last_name": "Perez", "age": 25}

Ejemplo: paciente Lopez Benito
Resultado: {"first_name": "Benito", "last_name": "Lopez", "age": null}

Ejemplo: Veronica 40 años
Resultado: {"first_name": Veronica, "last_name": null, "age": 40} \n\n''' + transcript

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.1,
        max_tokens=250,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    answer = response['choices'][0]['text']

    return answer


def upload_audio(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')
        # Process the audio file
        audio = convert_audio_format(audio_file, 'wav')

        # Create a temporary file to save the converted audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            temp_audio.write(audio.read())
            converted_file_path = temp_audio.name

        # Perform transcription using OpenAI's Audio API
        transcript = transcribe_audio(converted_file_path)

        # Remove the temporary converted audio file
        os.remove(converted_file_path)

        answer = get_answer(transcript)

        return JsonResponse({'transcription': linebreaksbr(transcript), 'answer': linebreaksbr(answer)})

    # Handle other request methods (PUT, DELETE, etc.)
    return JsonResponse({'message': 'Method not allowed'}, status=405)
