import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
# Recognizer instance
r  = sr.Recognizer()
path_name = 'assets/audio/lecture.wav'

def handle_large_audio(path):
    """
    Splitting the large audio file into chunks
    and apply speech recognition on each of these chunks

    Parameters
    ----------
    pathname: string
        The path to audio file

    Returns
    -------
    string
        The transcript of the audio 
    
    Raises
    ------
    UnknownValueError
        If the algoritm cannot transcribe the audio due to background noise

    Examples
    --------
    >>> handle_large_audio('assets/audio/lecture.wav')
    >>> chunk1.wav: Alright,let's talk about amphibians today
    >>> chunk2.wav: They are 
    """
    # Open audio file
    sound = AudioSegment.from_wav(path)
    # Split audio where silence is 1 second or more
    # Return chunks of sound
    chunks = split_on_silence(sound, min_silence_len= 100, silence_thresh=sound.dBFS-15,keep_silence=300)

    whole_text = ''
    # process each chunk 
    for i, audio_chunk in enumerate(chunks, start=1):
        # export audio chunk and save it in
        # the `folder_name` directory.
        chunk_filename = os.path.join('assets/audio', f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        # recognize the chunk
        with sr.AudioFile(chunk_filename) as source:
            r.adjust_for_ambient_noise(source)
            audio_listened = r.record(source)
            # try converting it to text
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                text = f"{text.capitalize()}. "
                print(chunk_filename, ":", text)
                whole_text += text

            # Remove the files after finishing the job
            os.remove(chunk_filename)
    # return the text for all chunks detected
    return whole_text


def write_to_file(text):
    with open('assets/out/recording.txt','w') as file:
        file.write(text)


if __name__ == "__main__":
    result = handle_large_audio(path_name)
    write_to_file(result)

