from gtts import gTTS

def gttsModule(text):
    tts = gTTS(text=text, lang='ko')
    tts.save("image_test/testSound.mp3")
    data = open("image_test/testSound.mp3", "rb").readlines()
    return data

def start(audio_id, text):
    if(audio_id == '1'):
        return gttsModule(text)
    elif(audio_id == '2'):
        print("sTTS is not defined")
        return gttsModule(text)
