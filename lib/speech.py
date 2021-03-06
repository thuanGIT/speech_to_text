import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import time

r  = sr.Recognizer()
FORMAT_TO_CONVERT= {'m4a','mp4','mp3'}
result_file = 'result.txt'

def handle_large_audio(self, filename=None):
    if filename is None:
        raise FileNotFoundError

    # Check the extension of the filepath
    format = filename[-3:]
    print(format)
    # Open audio file
    sound = AudioSegment.from_file(filename, format)

    # Convert file to wav if not
    if format in FORMAT_TO_CONVERT:
        sound = convert_to_wav(audio=sound, sourcepath=filename)


    # Split audio where silence is 1 second or more
    # Keep 300ms trailing/leading seconds
    # Anything less than -15 dBFS is considered silence
    # Return chunks of sound
    chunks = split_on_silence(sound, min_silence_len= 1000, silence_thresh=sound.dBFS-15,keep_silence=300)

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
                print(chunk_filename, "(done):", text)
                self.update_state(state='PROGRESS', 
                                    meta={'current': i, 'total': len(chunk_filename), 'status': text})

                # Appending the resulting transcript here
                whole_text += text

        # Remove the files after finishing the job
        os.remove(chunk_filename)

        time.sleep(1)
    # After finishing the job
    # Remove the audio file
    #os.remove('assets/audio/recording.wav')

    # Debugging
    print(whole_text)
    write_to_file(whole_text, filename=result_file)

    return {'current': 100, 'total': 100, 'status': 'Task completed', 'result': whole_text}

    


def write_to_file(text, filename):
    with open(f'assets/download/{filename}','w') as file:
        file.write(text)
        
def convert_to_wav(audio, sourcepath, savepath='assets/audio') -> AudioSegment:
    """
    Convert other audio formats to wav

    Parameters
    ----------
    audio: AudioSegment
        The AudioSegment Instance representing the audio file
    
    savepath: str
        Path to save file

    Returns
    -------
    AudioSegment
        Return a new AudioSegmnet instance pointing to the newly converted files in .wav
    
    Raises
    ------
    Exception
        In case some unexpected error happens.

    Examples
    --------
    >>> from pydub import AudioSegment
    >>> audio = AudioSegment.from_file('test.mp4', format = 'mp4')
    >>> convert_to_wav(audio, 'assets/audio/')
    >>> True 
    """
    try:
        audio.export(os.path.join(savepath,'recordings.wav'), format="wav")
        os.remove(sourcepath)
        return AudioSegment.from_wav(savepath)
    except Exception as e:
        print("Error: ", e)
        return audio

