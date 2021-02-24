# Speech To Text

- This project is dedicated as a gift to my friend. The main goal is to help reduce the stress of long lecture recordings.

- The application will serve as a tool to transcribe the audio file into textx file with audio transcript for notetaking.

## Description

- The backend services are built upon Flask library and Celery queue for background jobs.

- The application is hosted on Heroku cloud service and is still in developmental phase.

## Try it out

- Please go to this link to experience the app. [Click Here](https://speech-to-text-leah.herokuapp.com)

## How to test run on your local host

- Clone the repository with ``` git clone https://github.com/thuanGIT/speech_to_text.git```.

- Run ```cd speech_to_text``` to move to repo's current working directory.

- Install required dependences: ```pip install -r requirements.txt```

- Install redis CLI: ```brew install redis```. Note: You will have to install brew if you have not.

- Run the app: ```python3 main.py```

- Open another termnial session and open another thread for celery worker: ``` celery worker -A main.celery --loglevel=info```
