"""
Keybindings to be used by different functions. The key must be placed inside quotes
inside of ord(). Keys must also be the lowercase version.
Example:
    Good            Bad
    ord("w"):       ord("W")
"""

import curses

import exceptions
# Used for scrolling through post headers and a post


class Keybind:
    """Models a keybinding. Contains a description, which is a string describing what the key does.
    Ex: 'ScrollUp'. Also contains the actual key. Can be an integer or a single character string
    """

    def __init__(self, description: str, keys: int | str | list):
        self.keys = self.checkKey(keys)
        self.description = description

    def checkKey(self, keys: int | str | list):
        formatted = []
        if not isinstance(keys, list):
            keys = [keys]
        for key in keys:
            if isinstance(key, str):
                if len(key) > 1:
                    raise exceptions.KeyBindingError(
                        key=key,
                        msg=" is too long. Use a single character or an integer.",
                    )
                else:
                    key = ord(key)
            elif isinstance(key, int):
                if key < 0:
                    raise exceptions.KeyBindingError(
                        key=key, msg=". Negative key values are not allowed."
                    )
            else:
                raise exceptions.KeyBindingError(
                    key=key, msg=". Key must be of either str or int type."
                )
            formatted.append(key)
        return formatted


# Models scrolling up and down
scrollVerticalKeys = [
    Keybind(description="scrollUp", keys=[ord("w"), curses.KEY_UP]),
    Keybind(description="scrollDown", keys=[ord("s"), curses.KEY_DOWN]),
    Keybind(description="scrollTop", keys=[ord("t")]),
    Keybind(description="scrollBottom", keys=[ord("b")]),
]

# Models scrolling left and right
scrollHorizontalKeys = [
    Keybind(description="scrollLeft", keys=[ord("a"), curses.KEY_LEFT]),
    Keybind(description="scrollRight", keys=[ord("d"), curses.KEY_RIGHT]),
]

# Used for general controls, ex: exit/quit, refresh
controlKeys = [
    Keybind(description="exit", keys=[ord("q")]),
    Keybind(description="refresh", keys=[ord("r")]),
    Keybind(description="resize", keys=[curses.KEY_RESIZE]),
]

# Used for interacting with a post, such as image, url, etc.
postKeys = [
    Keybind(description="help", keys=[ord("h")]),
    Keybind(description="open", keys=[ord("o")]),
    Keybind(description="copy", keys=[ord("c")]),
    Keybind(description="message", keys=[ord("m")]),
    Keybind(description="url", keys=[ord("u")]),
    Keybind(description="image", keys=[ord("i")]),
]

# Used for editing something, ex: enter/select, add, delete
editKeys = [
    Keybind(description="enter", keys=[ord("e")]),
    Keybind(description="view", keys=[ord("w")]),
    Keybind(description="add", keys=[ord("a")]),
    Keybind(description="delete", keys=[ord("d")]),
]
"""          
scrollVerticalKeysDefault={
    curses.KEY_UP:"scrollUp",
    curses.KEY_DOWN:"scrollDown"
}

scrollVerticalKeys={
    ord("w"):"scrollUp",
    ord("s"):"scrollDown",
    ord("t"):"scrollTop",
    ord("b"):"scrollBottom",
}

# Used for scrolling between posts
scrollHorizontalKeys={
    ord("a"):"scrollLeft",
    ord("d"):"scrollRight"
}
scrollHorizontalKeysDefault={
    curses.KEY_LEFT:"scrollLeft",
    curses.KEY_RIGHT:"scrollRight"
}

# Used for controlling the terminal screen
controlKeys={
    ord("q"):"exit",
    ord("r"):"refresh",
    curses.KEY_RESIZE:"resize"
}

# Used for interacting with a post
postKeys={ 
    ord("h"):"help",
    ord("o"):"open",
    ord("c"):"copy",
    ord("m"):"message",
    ord("u"):"url",
    ord("i"):"image"
}

# Used for selecting a search and editing searches
editKeys={
    ord("e"):"enter",
    ord("v"):"view",
    ord("a"):"add",
    ord("d"):"delete"
}
"""
