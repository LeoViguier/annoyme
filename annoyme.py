import random, time, threading, os, pyautogui, re, shlex, sys, queue
from loguru import logger
from flask import Flask, render_template, request, send_from_directory
from waitress import serve
import tkinter as tk

# Configuration
COOLDOWN_TIME = 0 # seconds
LAST_ACTION_TIME = 0
ONLY_CUSTOM_SOUNDS = True
WINDOW = None

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


class TextDisplayManager:
    def __init__(self):
        self.message_queue = queue.Queue()
        self.window_active = False
        self.window_thread = None
        self.lock = threading.Lock()

    def enqueue_message(self, text):
        """Add a message to the queue for display"""
        self.message_queue.put(text)
        
        with self.lock:
            if not self.window_active:
                self.window_active = True
                self.window_thread = threading.Thread(target=self._run_window_thread)
                self.window_thread.daemon = True
                self.window_thread.start()
    
    def _run_window_thread(self):
        """Run the Tkinter window in its own thread"""
        root = tk.Tk()
        root.overrideredirect(True)  # Remove window decorations
        root.attributes("-topmost", True)  # Keep the window on top
        root.attributes("-transparentcolor", "white")  # Make the background transparent
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        canvas = tk.Canvas(root, bg="white", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        active_texts = []
        
        def check_messages():
            try:
                while True:
                    try:
                        text = self.message_queue.get_nowait()
                        text_obj = create_text_object(text)
                        active_texts.append(text_obj)
                        self.message_queue.task_done()
                    except queue.Empty:
                        break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
            
            root.after(100, check_messages)
        
        def create_text_object(text):
            font_size = random.randint(50, 100)
            speed = random.randint(3, 5)
            direction = random.choice(["left_to_right", "right_to_left"])
            
            if direction == "left_to_right":
                x = 0
            else:
                x = screen_width
                
            y = random.randint(0, screen_height - font_size)
            text_id = canvas.create_text(x, y, text=text, font=("Arial", font_size), fill="red")
            
            text_obj = {
                "id": text_id,
                "x": x,
                "y": y,
                "direction": direction,
                "speed": speed,
                "screen_width": screen_width,
                "screen_height": screen_height
            }
            
            move_text(text_obj)
            return text_obj
        
        def move_text(text_obj):
            if text_obj["direction"] == "left_to_right":
                text_obj["x"] += 3
                if text_obj["x"] > text_obj["screen_width"]:
                    remove_text(text_obj)
                    return
            else:
                text_obj["x"] -= 3
                if text_obj["x"] < 0:
                    remove_text(text_obj)
                    return
                    
            canvas.coords(text_obj["id"], text_obj["x"], text_obj["y"])
            root.after(text_obj["speed"], lambda: move_text(text_obj))
        
        def remove_text(text_obj):
            canvas.delete(text_obj["id"])
            if text_obj in active_texts:
                active_texts.remove(text_obj)
        
        def check_window_status():
            if not active_texts and self.message_queue.empty():
                with self.lock:
                    self.window_active = False
                root.destroy()
                return
            
            # Keep checking
            root.after(1000, check_window_status)
        
        check_messages()
        check_window_status()
        root.mainloop()
        
        with self.lock:
            self.window_active = False

# Create a global instance of the manager
text_manager = TextDisplayManager()

@app.route('/text', methods=['POST'])
def text():
    text = request.json['message']
    logger.info(f'Moving text: {text}')
    text_manager.enqueue_message(text)
    return '200'

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


@app.route('/all_actions', methods=['GET', 'POST'])
def all_actions():
    move_mouse()
    move_windows()
    open_random_applications()
    type_random_stuff()
    play_random_sounds()
    return '200'


@app.route('/icon.png')
def icon():
    return send_from_directory(os.path.join(app.root_path, 'templates'), 'icon.png', mimetype='image/png')


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
