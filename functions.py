# Libraries
from copy import deepcopy
import curses
import datetime
import math
import json
import prawcore
import pyperclip
import re
from datetime import timezone

# Provided
import search
import formatString
import scroll
import dump
import page as p
import editSearch
import exceptions
import keybindings as kb

import config


def close(screen):
    """
    Closes the ncurses window and restores the terminal to its previous state
    """
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()


def currentTimestamp():
    """
    Returns the current UTC timestamp
    """
    return datetime.datetime.now(timezone.utc).timestamp()


def getSearches(JSONPath):
    """
    Gathers all search objects that can be found in the JSONPath file
    """
    searches = []
    with open(JSONPath, "r") as read:
        data = json.load(read)
        s = data["searches"]
        read.close()

        for item in s:
            subs = item["subreddits"]
            subSearches = []
            for i in subs:
                name = i["name"]
                titleWL = i["whiteListTitle"]
                titleBL = i["blackListTitle"]
                flairWL = i["whiteListFlair"]
                flairBL = i["blackListFlair"]
                postWL = i["whiteListPost"]
                postBL = i["blackListPost"]
                subSearches.append(
                    search.SubredditSearch(
                        name, titleWL, titleBL, flairWL, flairBL, postWL, postBL
                    )
                )

            searches.append(
                search.Search(item["name"], item["lastSearchTime"], subSearches)
            )

    return searches


def getNumPosts(reddit, searchCriteria, numPosts=20):
    """
    reddit is the reddit instance, searchCriteria is a search object,
    and numPosts is the number of posts to fetch per subreddit in
    searchCriteria

    """
    posts = []
    for sub in searchCriteria.subreddits:
        subreddit = reddit.subreddit(sub.subreddit)
        for post in subreddit.new(limit=numPosts):
            posts.append(post)

    return posts


def listSearches(searches):
    """Returns a list of searches provided, each enumerated

    Args:
        searches (list): list of Search objects. Each Search object should have a name variable

    Returns:
        list: a list of strings of the format x.name
    """
    return [f"{n+1}. {searches[n].name}" for n in range(len(searches))]


def getSearchNum(screen, searches, minCols=80, minLines=24):
    """Displays a list of searches, and has the user select one to be performed.
    Also allows the user to create or delete searches.

    Args:
        screen (curses.screen): The screen to display output to
        searches (list): list of search objects that will be chosen from
        minCols (int, optional): Minimum number of columns to use. Defaults to 80.
        minLines (int, optional): Minimum number of rows to use. Defaults to 24.

    Returns:
        int:
            -3: Search was deleted, therefore save  
            -2: Searches parameter is empty, or the user selected to create a new search  
            -1: User pressed q to quit  
            \\>=0: The index of the searches list that was chosen  
    """
    if searches is not None:
        # Defines the different tooltips
        targets = ["add","enter","delete","view","exit"]
        bindingSet = kb.controlKeys + kb.editKeys
        matches = kb.findBindings(targets,bindingSet)
        toolTipTypes = {
            "main": [
                scroll.Line("", 0, curses.COLS),
                scroll.Line(
                    [
                        "<-- Line %i -- >",
                        f"({showKeyBind(matches[0])}) add, ({showKeyBind(matches[1])}) select, ({showKeyBind(matches[2])}) delete, ({showKeyBind(matches[3])}) view, or ({showKeyBind(matches[4])}) quit",
                    ],
                    [0, "max-55"],
                    curses.COLS,
                ),
            ],
            "press": [
                scroll.Line("", 0, curses.COLS),
                scroll.Line(
                    ["Enter a search number, then press enter: ", f"(press {showKeyBind(matches[4])} to exit)"],
                    [0, "max-18"],
                    curses.COLS,
                ),
            ],
            "enter": [
                scroll.Line("", 0, curses.COLS),
                scroll.Line(
                    ["Enter a search number, then press enter: ", f"(enter {showKeyBind(matches[4])} to exit)"],
                    [0, "max-18"],
                    curses.COLS,
                ),
            ],
        }
        mode = {
            "enter": "~Selecting~",
            "view": "~Viewing~",
            "delete": "~Deleting~",
        }
        toolTip = scroll.ToolTip(toolTipTypes["main"])

        # Creates the scrolling list page
        ls = listSearches(searches)
        scrollList = scroll.ScrollingList(screen, ls, 0, toolTip)
        page = p.Page(
            screen=screen,
            scrollingList=scrollList,
            tooltip=toolTip,
            tooltipTypes=toolTipTypes,
            onUpdate=listSearches,
            content=searches,
            minRows=minLines,
            minCols=minCols,
        )
        page.switchTooltip("main")

        while True:
            # Updates tooltip and prints page to screen
            page.refreshTooltip("main", page.currentLine() + 1, index=1, print=True)

            # Gets single character input from user
            char = eventListener(
                screen, bindings=[kb.controlKeys, kb.scrollVerticalKeys, kb.editKeys]
            )
            match char:
                case "timeout":
                    continue

                case "exit":  # Returns from function, signalling to quit program
                    return -1

                case "add":  # 'a' was pressed. Adds a search
                    return -2

                # User wants to perform, view, or delete a search
                case "enter" | "delete" | "view":
                    # Tells user to press 'q' to exit
                    page.refreshTooltip(
                        "press", page.currentLine() + 1, index=1, print=False
                    )
                    toolTip.update(scroll.Line(mode[char], 0, curses.COLS))
                    page.print()

                    # Moves cursor to end of prompt
                    placeCursor(screen, x=41, y=curses.LINES - 1)

                    # Gets a single character from user
                    c = screen.getch()  # Allows immediate exit if they press q
                    if c == ord("q"):
                        continue

                    # Tells user to enter 'q' to exit
                    page.refreshTooltip(
                        "enter", page.currentLine() + 1, index=1, print=False
                    )
                    page.tooltip.update(scroll.Line(mode[char], 0, curses.COLS))
                    page.print()

                    # Gets multi-character input from the user
                    string = getInput(
                        screen=screen,
                        page=page,
                        tooltip=toolTip,
                        unget=c,
                        col=41,
                    )

                    # Attempts to convert their input to an integer
                    val = 0
                    try:
                        val = int(string) - 1
                    except ValueError:
                        continue

                    # The val must be a valid index in the list of searches
                    if val >= 0 and val < len(searches):
                        if char == "delete":  # 'd' key for delete
                            del searches[val]
                            return -3
                        elif char == "view":  # Views search
                            status = viewSearch(screen,searches[val])
                            if status:
                                searches[val] = status
                            else:
                                return -3
                        else:  # Selects search
                            return val
                case _:
                    page.manipulate(char)
    else:
        return -2


def viewSearchUpdate(search):
    search.tree.cascading_update(set_fancy=config.fancy_characters)
    return search.tree.print(as_a_string=False)
    # return searchTree(search, curses.COLS, config.fancy_characters)


def viewSearch(screen, search, minCols=80, minLines=24):
    """
    Enters a screen with a tree depicting the specified search is displayed
    """

    if search is not None:
        toolTipType = "main"
        toolTipTypes = {
            "main": [
                scroll.Line("", 0, curses.COLS),
                scroll.Line(
                    ["<-- Line %i -- >", "press (e) to edit or (q) to exit"],
                    [0, "max-33"],
                    curses.COLS,
                ),
            ],
            "save": [
                scroll.Line(
                    ["Would you like to save? [Y/N]:", "(press enter)"],
                    [0, "max-14"],
                    curses.COLS,
                )
            ],
        }
        toolTip = scroll.ToolTip(toolTipTypes[toolTipType])

        view = viewSearchUpdate(search)
        page = scroll.ScrollingList(screen, view, 0, toolTip)
        viewPage = p.Page(
            screen=screen,
            scrollingList=page,
            tooltip=toolTip,
            tooltipTypes=toolTipTypes,
            onUpdate=viewSearchUpdate,
            content=search,
            minRows=minLines,
            minCols=minCols,
        )
        viewPage.switchTooltip("main")

        while True:
            # Changes toolTip if necessary
            viewPage.refreshTooltip(
                "main", viewPage.currentLine() + 1, index=1, print=True
            )

            # Gets input from user
            viewChar = eventListener(
                screen, bindings=[kb.controlKeys, kb.scrollVerticalKeys, kb.editKeys]
            )

            match viewChar:
                case "exit":  # Returns from function, signalling to exit search view
                    return False

                case "enter":
                    originalSearch = deepcopy(search)
                    resized = editSearch.EditSearch(screen, search, minCols, minLines)
                    if resized:
                        viewPage.resize()
                    else:
                        viewPage.updateContent()
                    viewPage.refreshTooltip("save", print=True)
                    answer = getInput(screen, col=31).lower()
                    if not (answer == "y" or answer == "yes"):
                        search = originalSearch
                        return originalSearch
                    else:
                        return False

                case _:
                    viewPage.manipulate(viewChar)


def getInput(
    screen, page=None, tooltip=None, prompt=None, unget=None, row=None, col=None
):
    """
    Gets multi-character input from the user and returns it.
    """
    if (
        prompt is not None and tooltip is not None
    ):  # Display the prompt for input that was specified
        if isinstance(prompt, list):
            tooltip.replace(prompt)
        else:
            tooltip.replace([prompt])
    if page is not None:
        page.print()

    # Places the curser at the end of the prompt, or where specified by row and col
    if row is None:
        if col is None:
            placeCursor(screen, x=(len(prompt) + 1), y=curses.LINES - 1)
        else:
            placeCursor(screen, x=col, y=curses.LINES - 1)
    else:
        if col is None:
            placeCursor(screen, x=(len(prompt) + 1), y=row)
        else:
            placeCursor(screen, x=col, y=row)

    # Gets input
    curses.echo()  # Displays what they type
    curses.nocbreak()  # Requires that they press enter
    if unget is not None:
        curses.ungetch(unget)
    string = screen.getstr().decode("ASCII")  # Their input

    # Undo displaying input and requiring enter be pressed
    curses.noecho()
    curses.cbreak()

    return string


def createSearch(screen, minCols=80, minLines=24):
    """
    Creates a search object found in search.py. Prompts user to input data to create this object
    """

    toolTipTypes = {
        "press": [
            scroll.Line(
                ['(name can not be "q")'],
                [0],
                curses.COLS,
            ),
            scroll.Line(
                ["Enter name of search, then press enter:", "(press q to exit)"],
                [0, "max-18"],
                curses.COLS,
            ),
        ],
        "enter": [
            scroll.Line(
                ['(name can not be "q")'],
                [0],
                curses.COLS,
            ),
            scroll.Line(
                ["Enter name of search, then press enter:", "(enter q to exit)"],
                [0, "max-18"],
                curses.COLS,
            ),
        ],
        "save": [
            scroll.Line(
                ["Would you like to save? [Y/N]:", "(press enter)"],
                [0, "max-14"],
                curses.COLS,
            )
        ],
    }
    toolTip = scroll.ToolTip(toolTipTypes["press"])
    scrollingList = scroll.ScrollingList(screen, [], tooltip=toolTip)

    page = p.Page(
        screen=screen,
        scrollingList=scrollingList,
        tooltip=toolTip,
        tooltipTypes=toolTipTypes,
        minRows=minLines,
        minCols=minCols,
    )
    page.refreshTooltip("press", print=True)

    placeCursor(screen, x=40, y=curses.LINES - 1)
    c = screen.getch()  # Gets the character they type
    if c == ord("q"):  # Immediately exits if they pressed q
        return None

    else:  # Otherwise
        # Update prompt to tell them to 'enter q" instead of 'press q"
        page.refreshTooltip("enter", print=True)
        name = getInput(screen, unget=c, col=40)
        if name.lower == "q":
            return None
        newSearch = search.Search(name)
        resized = editSearch.EditSearch(
            screen, newSearch, minCols=minCols, minLines=minLines
        )
        if resized:
            page.resize()
        else:
            page.updateContent()
        page.refreshTooltip("save", print=True)
        answer = getInput(screen, col=31).lower()
        if answer == "y" or answer == "yes":
            return newSearch
        else:
            return None


def completeSearch(
    reddit,
    searches,
    searchIndex,
    posts=None,
    screen=None,
    minCols=80,
    minLines=24,
    save=True,
    searchesPath=None,
):
    """
    Calls performSearch and saves the search timestamp to the searches file. Saving the timestamp can be disabled with the save parameter.
    """
    time = math.floor(currentTimestamp())
    posts = posts + performSearch(
        reddit, searches[searchIndex], screen, minCols, minLines
    )
    posts = sortPosts(posts)
    searches[
        searchIndex
    ].lastSearchTime = time  # Sets the search time in the search variable
    if save and searchesPath is not None:
        dump.saveSearches(
            searches, searchesPath
        )  # Writes the search variable to the file
    return posts


def performSearch(reddit, search, screen=None, minCols=80, minLines=24):
    """
    Gathers posts that meat the search object criteria, using the reddit object.
    If a screen object is provided, displays a simple search in progress message.
    """
    posts = []
    ticker = 0
    if screen is not None:
        screen.clear()
        screen.refresh()
        string = "Searching..."
        stringTicker = 0
    for sub in search.subreddits:
        subreddit = reddit.subreddit(sub.name)
        for post in subreddit.new(
            limit=None
        ):  # Gets all posts in the current subreddit
            if post.created_utc is None:
                continue
            if (
                post.created_utc < search.lastSearchTime
            ):  # continues until it finds a post older than the last search time
                break
            else:
                if filterPost(
                    post, sub
                ):  # If post meets the specified filters, append it to the list
                    posts.append(post)
            ticker = ticker + 1

            if screen is not None:
                resize = eventListener(
                    screen, bindings=[kb.controlKeys], characters=False, timeout=5
                )  # Gets input from user. Only listens for terminal resizing

                if resize == "resize":  # Resizes content if terminal was resized
                    size = list(screen.getmaxyx())
                    if size[0] < minLines:
                        size[0] = minLines
                    if size[1] < minCols:
                        size[1] = minCols
                    curses.resize_term(size[0], size[1])

                screen.clear()
                waitMessage = "(This may take a while, depending on time since the search was last performed)"
                # Prints the wait message at the bottom of the screen
                screen.addstr(
                    curses.LINES - 1,
                    int((curses.COLS - len(waitMessage)) / 2),
                    waitMessage,
                )

                # Displays searching... in the middle of the screen, with an animation.
                # starts with s, and adds characters after that, then once it reaches the end of the string,
                # starts removing characters from the beginning of the string. Once
                # no characters remain, starts over

                stringTicker = int(ticker / 98)
                stringTicker = stringTicker % (len(string) * 2)
                if stringTicker >= len(string):
                    screen.addstr(
                        int((curses.LINES / 2) - 1),
                        int((curses.COLS - len(string)) / 2)
                        + stringTicker
                        - len(string),
                        string[stringTicker - len(string) :],
                    )
                else:
                    screen.addstr(
                        int((curses.LINES / 2) - 1),
                        int((curses.COLS - len(string)) / 2),
                        string[:stringTicker],
                    )

                screen.refresh()

    return posts


def filterPost(post, subSearch):
    """
    Determines if the post should be included, based off of the filters. Blacklisted items are removed before
    whitelisted items are added.
    """

    # Easier reference to post contents
    title = post.title
    flair = post.link_flair_text
    content = post.selftext

    # Check blacklists

    if title is not None and subSearch.titleBL is not None:
        for t in subSearch.titleBL.content:
            if t.lower() in title.lower():
                return False

    if flair is not None and subSearch.flairBL is not None:
        for f in subSearch.flairBL.content:
            if f.lower() in flair.lower():
                return False

    if content is not None and subSearch.postBL is not None:
        for c in subSearch.postBL.content:
            if c.lower() in content.lower():
                return False

    # Check whitelists

    if title is not None and subSearch.titleWL is not None:
        for t in subSearch.titleWL.content:
            if t.lower() in title.lower():
                return True

    if flair is not None and subSearch.flairWL is not None:
        for f in subSearch.flairWL.content:
            if f.lower() in flair.lower():
                return True

    if content is not None and subSearch.postWL is not None:
        for c in subSearch.postWL.content:
            if c.lower() in content.lower():
                return True

    return False


def getHeaders(posts):
    """
    Formats and returns post header information. This includes: subreddit, title, flair, author, and age
    """
    headers = []
    ticker = 1
    if posts is not None:
        for post in posts:  # Loops through each post
            info = getPostInfo(post)  # Gets the information about the post

            try:
                headers += formatString.enbox(  # Enboxes and stores the results
                    [
                        f"{ticker}). {info['title']}",
                        info["author"],
                        info["flair"],
                        f"Posted in ({info['sub']}), {info['age']}",
                    ],
                    curses.COLS,
                    fancy=config.fancy_characters,
                )
            except AttributeError:
                continue
            ticker += 1
    return headers


def sortPosts(posts):
    """
    Sorts a list by creation date. The newest posts come first
    """
    posts.sort(key=postAge, reverse=True)
    return posts


def postAge(post):
    """
    Provides the creation time of a post, in UTC
    """
    return post.created_utc


def copyToClipboard(string):
    """
    Copies the string to the clipboard
    """
    pyperclip.copy(string)


def getPostInfo(post):
    """
    Returns basic information about a post, including age, subreddit it was posted into, title, flair, and author
    """
    # Age
    age = "<NONE>"
    if post.created_utc is not None:
        age = (
            f"{formatString.formatAge(int(currentTimestamp()-post.created_utc),'ago')}"
        )

    # Subreddit
    sub = formatString.removeNonAscii(post.subreddit.display_name)
    if sub is None:
        sub = "<NO SUBREDDIT>"

    # Title
    title = formatString.removeNonAscii(post.title)
    if title is None:
        title = "<NO TITLE>"

    # Flair
    flair = formatString.removeNonAscii(f"~Flair: {post.link_flair_text}~")
    if flair is None:
        flair = "~<NO FLAIR>~"

    # Author
    author = post.author
    if author is None:
        author = "[deleted]"
    else:
        author = f"[{author.name}]"

    return {"age": age, "sub": sub, "title": title, "flair": flair, "author": author}







def showKeyBind(bind: kb.Keybind | None) -> str:
    """Returns the first key in the keybind.

    Args:
        bind (kb.Keybind | None): keybind object being examined

    Returns:
        str: the first key in keybind.key, as a single character string
    """
    return "undefined" if bind is None else chr(bind.keys[0])








def findURLs(text):
    """
    Returns a list of all the valid urls in the text
    """
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, text)
    return [x[0] for x in url]


def placeCursor(screen, x, y):
    """
    Moves the cursor to the specified location
    """
    screen.addstr(y, x, "")


def isValidSubreddit(userReddit, name):
    """
    Pulls a single post from the subreddit specified in name, using the praw reddit instance userReddit.
    Returns 1 if sub is valid, -1 if it does not exist or has been banned, or -2 if it is private
    """
    try:
        for submission in userReddit.subreddit(name).new(limit=1):
            submission.id  # Attempts to pull a submission from the subreddit
    except (
        prawcore.exceptions.NotFound,
        prawcore.exceptions.Redirect,
        prawcore.exceptions.BadRequest,
        AttributeError,
    ):  # Errors that arise when the subreddit does not exist
        return -1
    except prawcore.exceptions.Forbidden:
        return -2
    return 1


def eventListener(
    screen, bindings: list | dict = None, characters=True, anyChar=False, timeout=100
):
    """
    Waits for a single character input from the user.
    bindings: a list of lists of Keybind objects. Returns the first match.
    characters: is whether it will listen for characters for input, or just terminal resizing.
    anyChar: will return any for any character input.
    timeout: is the number of milliseconds the function will wait for a response before returning timeout.
    """

    if bindings is None and not anyChar:
        raise exceptions.NoBindingError
    if isinstance(bindings, dict):
        bindings = [bindings]
    try:
        screen.timeout(timeout)
        char = screen.getch()
        if char == curses.KEY_RESIZE:
            screen.timeout(-1)
            return "resize"
        elif anyChar:
            retVal = ""
            if char == -1:
                retVal = "timeout"
            else:
                retVal = "any"
            screen.timeout(-1)
            return retVal
        elif characters:
            if not bindings:
                screen.timeout(-1)
                raise exceptions.NoBindingError
            else:
                for item in bindings:
                    for binding in item:
                        if char in binding.keys:
                            screen.timeout(-1)
                            return binding.description
        else:
            screen.timeout(-1)
            return "timeout"
    except curses.error:
        screen.timeout(-1)
        return "timeout"
