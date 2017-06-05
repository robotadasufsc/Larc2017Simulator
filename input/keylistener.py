from input import pyxhook

class KeyListener:
    """
    This class hooks into keyboard events, and saves the states of each key into a dictionary.
    """
    keyMap = {}

    def pressed(self, event):
        self.keyMap[event.Ascii] = True

    def released(self, event):
        self.keyMap[event.Ascii] = False

    def __getitem__(self, key):
        key_number = ord(key)
        if key_number in self.keyMap:
            return self.keyMap[key_number]
        else:
            return False

    def __init__(self):
        self.hookman = pyxhook.HookManager()
        self.hookman.KeyDown = self.pressed
        self.hookman.KeyUp = self.released
        self.hookman.HookKeyboard()
        self.hookman.start()

    def __del__(self):
        self.hookman.cancel()


if __name__ == "__main__":
    KeyListener()
