import audioop
import os
import re
import time
from threading import Thread

import pyttsx3
import requests
from pydub import AudioSegment
from pymumble_py3 import Mumble
from pymumble_py3.errors import UnknownChannelError

DATAURL = 'http://43.133.206.230:20350/data.json'

RATE = 135

VOLUME = 0.8

LISTPLAYING = []

currNum = 0


def clear_directory(directory):
    # 获取目录中的所有文件和子目录
    for root, dirs, files in os.walk(directory):
        # 删除所有文件
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)


def replaceLR(string):
    pattern = r'(\d+)([RL])'
    replacement = lambda match: match.group(1) + ('Right' if match.group(2) == 'R' else 'Left')
    result = re.sub(pattern, replacement, string)
    return result


def proceedText(text: str):
    text = replaceLR(text)
    text = text.replace('m/s', 'meters per second').replace('deg C', 'Celsius').replace('deg F', 'Fahrenheit') \
        .replace('mph', 'miles per hour').replace('kts', 'knots')
    text = text.replace('RNAV', 'r natf').replace('hPa', 'hectopascals')
    text = text.replace('1', 'one ').replace('2', 'two ').replace('3', 'three ').replace('4', 'four ') \
        .replace('5', 'five ').replace('6', 'six ').replace('7', 'seven ').replace('8', 'eight ') \
        .replace('9', 'nine ').replace('0', 'zero ')
    text = text.replace('\n', '')
    text = text.replace('A,', 'Alpha,').replace('B,', 'Bravo,').replace('C,', 'Charlie,').replace('D,', 'Delta,') \
        .replace('E,', 'Echo,').replace('F,', 'Foxtrot,').replace('G,', 'Golf,').replace('H,', 'Hotel,') \
        .replace('I,', 'India,').replace('J,', 'Juliett,').replace('K,', 'Kilo,').replace('L,', 'Lima,') \
        .replace('M,', 'Mike,').replace('N,', 'November,').replace('O,', 'Oscar,').replace('P,', 'Papa,')
    text = text.replace('Q,', 'Quebec,').replace('R,', 'Romeo,').replace('S,', 'Sierra,').replace('T,', 'Tango,')
    text = text.replace('U,', 'Uniform,').replace('V,', 'Victor,').replace('W,', 'Whiskey,').replace('X,', 'Xray,')
    text = text.replace('Y,', 'Yankee,').replace('Z,', 'Zulu,')
    text = text.replace('CAVOK', 'carve ok')
    text = text.replace(' ,', ', ')
    # print(text)
    return text


def getMP3(callsign,freq, text):
    engine = pyttsx3.init()
    engine.setProperty('rate', RATE)
    engine.setProperty('volume', VOLUME)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.save_to_file(text, f'./sounds/{callsign}--{freq}.mp3')
    engine.runAndWait()
    engine.stop()


def play():
    global currNum
    for root, dirs, files in os.walk('./pcms'):
        for file in files:
            if file in LISTPLAYING:
                continue
            currNum += 1
            if currNum >= 50:
                currNum = 0
            Thread(target=playThread, args=(file,)).start()


def playThread(file):
    LISTPLAYING.append(file)
    try:
        print(file.removesuffix('.pcm')+" logon")
        m = Mumble('43.154.178.153', f'atis{currNum}', port=14514, password='qaz114514', reconnect=True, debug=False)
        m.start()
        m.is_ready()
        freq = file.split('--')[1].removesuffix('.pcm')
        m.users.myself.comment(file.split('--')[0])
    except:
        LISTPLAYING.remove(file)
        return

    while 1:
        try:
            channel = m.channels.find_by_name(freq)
            channel.set_channel_description(float(freq).__str__())
            channel.move_in()
            if m.my_channel()['name']!=freq:
                continue
            break
        except Exception as err:
            m.channels.new_channel(0, freq, temporary=True)
            time.sleep(1)
    try:
        while 1:
            with open(f'./pcms/{file}', 'rb') as f:
                pcm = f.read()
                i = 0
            while i < len(pcm):
                while m.sound_output.get_buffer_size() > 0.5:
                    time.sleep(0.01)
                m.sound_output.encoder_framesize = m.sound_output.audio_per_packet
                m.sound_output.add_sound(audioop.mul(pcm[i:i + 480], 2, 0.5))
                i += 480
            if not os.path.exists(f'./pcms/{file}'):
                break
        m.stop()
    except Exception as ec:
        print(ec)
    finally:
        LISTPLAYING.remove(file)
        m.stop()


def transToPCM():
    clear_directory('./pcms')
    for root, dirs, files in os.walk('./sounds'):
        for file in files:
            audio = AudioSegment.from_file(f'./sounds/{file}')
            audio = audio.set_frame_rate(48000)
            cs = f'{file.split(".")[0]}.{file.split(".")[1]}'
            audio.export(f'./pcms/{cs}.pcm', format="s16le", codec="pcm_s16le")


while 1:
    try:
        data = requests.get(DATAURL).json()
        atis = data['atis']
        clear_directory('./sounds')
        for each in range(len(atis)):
            text = proceedText(' '.join(atis[each]['text_atis']))
            getMP3(atis[each]['callsign'],atis[each]['frequency'], text)
        transToPCM()
        play()
    except Exception as e:
        print(e)
    time.sleep(10)
