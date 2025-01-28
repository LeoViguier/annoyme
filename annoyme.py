import random, time, threading, os, pyautogui, re, shlex, sys
from loguru import logger
from flask import Flask, render_template, request
from waitress import serve
import tkinter as tk

# Configuration
COOLDOWN_TIME = 0 # seconds
LAST_ACTION_TIME = 0
ONLY_CUSTOM_SOUNDS = True

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


class MovingText:
    def __init__(self, root : tk.Tk, text):
        self.root = root
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes("-topmost", True)  # Keep the window on top
        self.root.attributes("-transparentcolor", "white")  # Make the background transparent

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.text = text
        self.font_size = random.randint(50, 100)
        self.speed = random.randint(3, 5) # adjust based on the speed you want the text to move

        self.canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.direction = random.choice(["left_to_right", "right_to_left"])
        if self.direction == "left_to_right":
            self.x = 0
        else:
            self.x = self.screen_width

        self.y = random.randint(0, self.screen_height - self.font_size)

        self.text_id = self.canvas.create_text(self.x, self.y, text=self.text, font=("Arial", self.font_size), fill="red")

        self.move_text()

    def move_text(self):
        if self.direction == "left_to_right":
            self.x += 3 # Adjust based on your screen refresh rate
            if self.x > self.screen_width:
                self.root.destroy()  # Close the window when text goes off-screen
                return
        else:
            self.x -= 3
            if self.x < 0:
                self.root.destroy()
                return

        self.canvas.coords(self.text_id, self.x, self.y)
        self.root.after(self.speed, self.move_text)


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
    for app in random.choices(apps, k=3):
        os.system(f'start {app}')
        time.sleep(.1)

def type_random_stuff():
    pyautogui.write('azerqdfcvb', interval=0.1) # flash in league, use spells, back etc..
    pyautogui.press('enter')
    time.sleep(1)

def play_random_sounds():
    if ONLY_CUSTOM_SOUNDS:
        file = random.choice([i for i in os.listdir(os.path.join(path, 'sounds')) if "custom_" in i])
    else:
        file = random.choice(os.listdir(os.path.join(path, 'sounds')))
    sound = os.path.join(path, 'sounds', file)
    command = f'powershell -command "$PlayWav=New-Object System.Media.SoundPlayer; $PlayWav.SoundLocation=\'{sound}\'; $PlayWav.playsync()"'
    os.system(command)

def annoy():
    actions = [move_mouse, move_windows, open_random_applications, type_random_stuff, play_random_sounds]
    actions_probability = [.125, .125, .125, .125, .5]
    choice = random.choices(actions, actions_probability)[0]
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


def display_text(text):
    root = tk.Tk()
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    app = MovingText(root, text)
    root.mainloop()


@app.route('/text', methods=['POST'])
def text():
    text = request.json['message']
    logger.info(f'Moving text: {text}')
    threading.Thread(target=display_text, args=(text,)).start()

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
    global LAST_ACTION_TIME
    current_time = time.time()
    if current_time - LAST_ACTION_TIME > COOLDOWN_TIME:
        threading.Thread(target=annoy).start()
        LAST_ACTION_TIME = current_time
        return "200"
    else:
        logger.error('Cooldown time not reached')
        return "429"

if __name__ == '__main__':
    port = 9876
    logger.info(f'Server running on http://localhost:{port}/')
    serve(app, host='0.0.0.0', port=port)
