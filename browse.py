import functions
import scroll
import page as p
import curses
import keybindings as kb



def browsePosts(posts, screen, minCols=80, minLines=24):
    targets = ["enter","exit"]
    bindingSet = kb.controlKeys + kb.editKeys
    matches = kb.findBindings(targets,bindingSet)
    toolTipType = "main"
    toolTipTypes = {
        "main": [
            scroll.Line(
                ["<-- Line %i/%i -- >", f"(press {functions.showKeyBind(matches[0])} to view a post or {functions.showKeyBind(matches[1])} to quit)"],
                [0, "max-38"],
                curses.COLS,
            )
        ],
        "press": [
            scroll.Line(
                ["Enter a post number (1-%i), then press enter:", f"(press {functions.showKeyBind(matches[1])} to exit)"],
                [0, "max-18"],
                curses.COLS,
            )
        ],
        "enter": [
            scroll.Line(
                ["Enter a post number (1-%i), then press enter:", f"(enter {functions.showKeyBind(matches[1])} to exit)"],
                [0, "max-18"],
                curses.COLS,
            )
        ],
    }
    toolTip = scroll.ToolTip(toolTipTypes[toolTipType])
    page = scroll.ScrollingList(screen, functions.getHeaders(posts), tooltip=toolTip)

    browsePage = p.Page(
        screen=screen,
        scrollingList=page,
        tooltip=toolTip,
        tooltipTypes=toolTipTypes,
        onUpdate=functions.getHeaders,
        content=posts,
        minRows=minLines,
        minCols=minCols,
    )
    browsePage.switchTooltip("main")
    # browsePage.updateContent()

    while True:
        # Updates the tooltip, and prints the headers to the screen
        browsePage.refreshTooltip(
            "main", [browsePage.currentLine() + 1, page.maxLine + 1], print=True
        )

        # Gets input from the user

        input = functions.eventListener(
            screen, bindings=[kb.controlKeys, kb.scrollVerticalKeys, kb.editKeys]
        )

        match input:
            case "timeout":
                continue
            case "exit":
                break
            case "refresh":
                return -2
            case "enter":
                # Updates the tooltip and places the cursor for input
                browsePage.refreshTooltip("press", (len(posts)), print=True)

                functions.placeCursor(screen, x=48, y=curses.LINES - 1)
                c = screen.getch()  # Gets the character they type
                if c == ord("q"):  # Immediately exits if they pressed q
                    continue

                else:  # Otherwise
                    # Update prompt to tell them to 'enter q" instead of 'press q"
                    browsePage.refreshTooltip("enter", (len(posts)), print=True)
                    string = functions.getInput(
                        screen=screen, page=page, tooltip=toolTip, unget=c, col=48
                    )

                    # Attempts to convert their input into an integer.
                    val = 0
                    try:
                        val = int(string) - 1
                    except ValueError:
                        continue

                    # If the input was an integer, converts to an index, and checks if it is within the bounds of post numbers
                    # val -= 1
                    if val >= 0 and val < len(posts):
                        return val  # Index of the post to be viewed
            case _:
                browsePage.manipulate(input)
    return -1
