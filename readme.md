# AnnoyMe

Do you have a long distance girlfriend whose love language is annoying you ?
Do you spend too much time on your computer and not enough caring about her ?
Are you still asking chatGPT for advice on what gift to get her ?

Well, look no further, AnnoyMe is here to help you out. AnnoyMe is a simple python web server that listens for requests, and will do stuff on your computer to annoy you.

This will:
- Move your mouse around
- Move your windows around
- Open random applications
- Type random stuff
- Play random notification sounds
- TTS message
- All of them at the same time !

You can configure a cooldown time to prevent it from being too annoying, but don't tell her.

## Installation

You may use any version of python 3.7 or higher to make it work.
```bash
git clone https://github.com/LeoViguier/annoyme.git
cd annoyme
pip install -r requirements.txt
```

## Usage

```bash
python annoyme.py
```
If you want to add sounds, you can put `.wav` files in the `sounds` folder.
