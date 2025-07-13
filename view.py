# Functions used for viewing a post.
from io import BytesIO
import functions
import formatString
import scroll
import requests
import page as p
import keybindings as kb
import webbrowser
from PIL import Image
import PIL
import curses
import config

def viewPostUpdate(content):
    """
    Used by viewPost to re-enbox its content. Necessary for its resize function
    """
    return formatString.enbox(
        content,
        curses.COLS,
        fancy=config.fancy_characters,
    )

def viewPost(post, screen, minCols=80, minLines=24):
    """
    Enters a viewing mode for a single post. Arrow keys can be used to move through and between posts.
    """

    # Gets information about the post, and puts it into the form for viewing
    info = functions.getPostInfo(post)
    content = [
        info["title"],
        info["author"],
        info["flair"],
        f"Posted in ({info['sub']}), {info['age']}",
        "%separator%",
        formatString.removeNonAscii(post.selftext),
        "%separator%",
        post.url,
    ]
    try:
        stringList = viewPostUpdate(content)  # Enboxes the content
    except AttributeError:
        stringList = ""
    
    # Sets the tooltip
    targets = ["enter","exit"]
    bindingSet = kb.controlKeys + kb.editKeys
    matches = kb.findBindings(targets,bindingSet)

    toolTipType = "main"
    toolTipTypes = {
        "main": [
            scroll.Line(
                ["<-- Line %i/%i -- >", f"press ({functions.showKeyBind(matches[1])}) to exit"],
                [0, "max-18"],
                curses.COLS,
            )
        ]
    }
    toolTip = scroll.ToolTip(toolTipTypes[toolTipType])

    # Creates a page with the content and tooltip
    page = scroll.ScrollingList(screen, stringList, 0, toolTip)
    viewPage = p.Page(
        screen=screen,
        scrollingList=page,
        tooltip=toolTip,
        tooltipTypes=toolTipTypes,
        onUpdate=viewPostUpdate,
        content=content,
        minRows=minLines,
        minCols=minCols,
    )
    viewPage.switchTooltip("main")

    skip = False  # Stores whether gathering a character should be done. Used when exiting from the help screen

    while True:
        if not skip:  # Refreshes the tooltip's line number and gets input
            viewPage.refreshTooltip(
                "main", [viewPage.currentLine() + 1, page.maxLine + 1], 0, print=True
            )
            input = functions.eventListener(
                screen,
                bindings=[
                    kb.controlKeys,
                    kb.scrollHorizontalKeys,
                    kb.scrollVerticalKeys,
                    kb.postKeys,
                ],
            )
        skip = False

        match input:
            # User didn't enter anything within the window, repeats loop
            case "timeout":
                continue

            # Exits function
            case "exit":
                return 0

            # Returns value specifying to view previous post
            case "scrollLeft":
                return -1

            # Returns value specifying to view next post
            case "scrollRight":
                return 1

            # Displays a help screen
            case "help":
                screen.clear()
                tar = [
                    "scrollUp",
                    "scrollDown",
                    "scrollLeft",
                    "scrollRight",
                    "help",
                    "image",
                    "open",
                    "copy",
                    "url",
                    "message",
                ]
                bindingSet = (
                    kb.editKeys
                    + kb.postKeys
                    + kb.scrollVerticalKeys
                    + kb.scrollHorizontalKeys
                )

                # bindings = [bind for bind in bindingSet if bind.description in tar]

                # matches = bindingLookup(bindings, tar)
                matches = kb.findBindings(target=tar,bindingSet=bindingSet)

                helpPage = scroll.ScrollingList(
                    screen,
                    [
                        "Press the button in () to execute its command",
                        f"({functions.showKeyBind(matches[0])}) or (up arrow) scroll up",
                        f"({functions.showKeyBind(matches[1])}) or (down arrow) scroll down",
                        f"({functions.showKeyBind(matches[2])}) or (left arrow) view previous post",
                        f"({functions.showKeyBind(matches[3])}) or (right arrow) view next post",
                        f"({functions.showKeyBind(matches[4])}) Displays this menu",
                        f"({functions.showKeyBind(matches[5])}) If post is an image, opens image",
                        f"({functions.showKeyBind(matches[6])}) Opens the post in a new tab of the default web browser",
                        f"({functions.showKeyBind(matches[7])}) Copies the post url to the clipboard",
                        f"({functions.showKeyBind(matches[8])}) Prints the post urls to a file. (link_output in config.py)",
                        f"({functions.showKeyBind(matches[9])}) Opens the author's page in a new tab of the default web browser",
                        "Press any key to exit this screen",
                    ],
                    0,
                    None,
                )
                functions.placeCursor(screen, x=0, y=curses.LINES - 1)
                helpPage.print()
                while True:
                    char = functions.eventListener(
                        screen, bindings=[kb.controlKeys], anyChar=True
                    )  # Screen stays up until user does some action
                    if not (char == "timeout"):
                        if char == "resize":
                            skip = True
                        else:
                            skip = False
                        break
            # Open post in web browser
            case "open":
                webbrowser.open_new_tab(post.url)

            # Copy url to clipboard
            case "copy":
                functions.copyToClipboard(post.url)

            # Open image, if present
            case "image":
                response = requests.get(post.url)  # Gets information from Internet
                if (
                    response.status_code == 200
                ):  # Code 200 means information was sucessfully gathered
                    try:
                        img = Image.open(
                            BytesIO(response.content)
                        )  # Converts binary data to image
                        img.show()  # Opens the image in default image viewer
                    except (
                        PIL.UnidentifiedImageError
                    ):  # Typically thrown if the link was not an image.
                        pass

            # Open author's page
            case "message":
                webbrowser.open_new_tab(
                    f"https://www.reddit.com/user/{post.author.name}/"
                )

            # Displays url of post
            case "url":
                links = functions.findURLs(post.selftext)
                with open(config.link_output, "a") as f:
                    f.write(f"{info['title']}:\n")
                    f.write(f"\t{post.url}\n")
                    for link in links:
                        f.write(f"\t{link}\n")

                screen.clear()
                screen.addstr(0, 0, f"URLs saved to {config.link_output}")
                screen.addstr(
                    curses.LINES - 1, curses.COLS - 24, "(press any key to exit)"
                )
                functions.placeCursor(screen, x=0, y=curses.LINES - 1)
                screen.refresh()
                while True:
                    char = functions.eventListener(
                        screen, bindings=[kb.controlKeys], anyChar=True
                    )  # Screen stays up until user does some action
                    if not (char == "timeout"):
                        if char == "resize":
                            skip = True
                        else:
                            skip = False
                        break

            case _:
                viewPage.manipulate(input)
