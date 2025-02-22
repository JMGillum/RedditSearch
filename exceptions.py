class NoBindingError(Exception):
    def __init__(self, msg="No keybindings were specified"):
        self.msg = msg

    def __str__(self):
        return self.msg


class KeyBindingError(Exception):
    def __init__(self, key=None, msg=None):
        self.msg = msg

    def __str__(self):
        if self.key is not None:
            if self.msg is not None:
                return f"{self.key}{self.msg}"
            else:
                return f"{self.key} is not valid for a keybinding"
        else:
            if self.msg is not None:
                return self.msg
            else:
                return "The key is not valid for a keybinding"
