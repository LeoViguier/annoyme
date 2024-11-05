import random
import time
import threading
import os

import pyautogui
from flask import Flask, render_template, request
from waitress import serve

path = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

# Configuration
cooldown_time = 300  # seconds
last_action_time = 0

def move_mouse():
    for _ in range(10):
        x = random.randint(0, pyautogui.size().width)
        y = random.randint(0, pyautogui.size().height)
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.1)

def move_windows():
    for _ in range(2):
        pyautogui.hotkey('win', 'd')
        time.sleep(0.5)
        pyautogui.hotkey('win', 'd')
        time.sleep(0.5)
        pyautogui.hotkey('alt', 'tab')
        time.sleep(0.5)

def open_random_applications():
    apps = ['notepad', 'calc', 'mspaint', 'cmd', 'control', 'snippingtool']
    for app in apps:
        os.system(f'start {app}')
        time.sleep(.1)

def type_random_stuff():
    pyautogui.write('azerqdfcvb', interval=0.1) # flash in league, use spells, back etc..
    pyautogui.press('enter')
    time.sleep(1)

def play_random_sounds():
    file = random.choice(os.listdir(os.path.join(path, 'sounds')))
    sound = os.path.join(path, 'sounds', file)
    command = f'powershell -command "$PlayWav=New-Object System.Media.SoundPlayer; $PlayWav.SoundLocation=\'{sound}\'; $PlayWav.playsync()"'
    os.system(command)

def annoy():
    actions = [move_mouse, move_windows, open_random_applications, type_random_stuff, play_random_sounds]
    random.choice(actions)()

@app.route('/tts', methods=['POST'])
def tts():
    text = request.json['message']
    os.system(f'powershell -command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\')"')
    return '200'

@app.route('/all_actions', methods=['POST'])
def all_actions():
    move_mouse()
    move_windows()
    open_random_applications()
    type_random_stuff()
    play_random_sounds()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/annoyme', methods=['POST'])
def handle_annoy():
    global last_action_time
    current_time = time.time()
    if current_time - last_action_time > cooldown_time:
        threading.Thread(target=annoy).start()
        last_action_time = current_time
        return "200"
    else:
        return "429"

if __name__ == '__main__':
    print('Server running on http://localhost:9876/')
    serve(app, host='0.0.0.0', port=9876)
