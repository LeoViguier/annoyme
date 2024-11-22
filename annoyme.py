import random, time, threading, os, pyautogui, re, shlex, sys
from loguru import logger
from flask import Flask, render_template, request
from waitress import serve

# Configuration
cooldown_time = 0 # seconds
last_action_time = 0

path = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

log_format_stdout = (
    "{time:YYYY-MM-DD HH:mm:ss} | "
    "<level>{level: <8}</level> | "
    "<level>{message}</level>"
)
log_format_file = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
    "<level>{message}</level>"
)
logger.remove()
logger.add(sys.stdout, format=log_format_stdout, level="INFO", colorize=True, backtrace=True, diagnose=True)
logger.add(os.path.join(path, 'log/logs.log'), rotation='1 MB', retention='10 days', level='INFO', format=log_format_file)


@app.before_request
def log_request():
    logger.info(f"Request: {request.remote_addr} -> {request.url}")

def move_mouse():
    for _ in range(10):
        x = random.randint(0, pyautogui.size().width)
        y = random.randint(0, pyautogui.size().height)
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.1)

def move_windows():
    for _ in range(3):
        n = ['tab'] * random.randint(1, 5)
        pyautogui.hotkey('alt', *n)
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
    choice = random.choice(actions)
    logger.info(f'Performing action: {choice.__name__}')
    choice()

@app.route('/tts', methods=['POST'])
def tts():
    text = request.json['message']
    text = re.sub(r'[^a-zA-Z0-9 .,?!]+', '', text)
    text = shlex.quote(text)
    try:
        os.system(f'powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\')"')
    except:
        return '500'
    return '200'

@app.route('/all_actions', methods=['GET', 'POST'])
def all_actions():
    move_mouse()
    move_windows()
    open_random_applications()
    type_random_stuff()
    play_random_sounds()
    return '200'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/annoyme', methods=['GET', 'POST'])
def handle_annoy():
    global last_action_time
    current_time = time.time()
    if current_time - last_action_time > cooldown_time:
        threading.Thread(target=annoy).start()
        last_action_time = current_time
        return "200"
    else:
        logger.error('Cooldown time not reached')
        return "429"

if __name__ == '__main__':
    port = 9876
    logger.info(f'Server running on http://localhost:{port}/')
    serve(app, host='0.0.0.0', port=port)
