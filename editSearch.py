import curses

import config
import functions
import page as p
import scroll
import search
import tree
import keybindings as kb


class EditSearch:
    def __init__(self, screen, search, minCols=80, minLines=24, launch=True):
        self.update(screen, search, minCols, minLines)
        self.subreddit = None

        if launch:
            return self.launch()

    def update(self, screen=None, search=None, minCols=None, minLines=None):
        if screen is not None:
            self.screen = screen
        if search is not None:
            self.search = search
        if minCols is not None:
            self.minCols = minCols
        if minLines is not None:
            self.minLines = minLines

    def launch(self):
        self.editSearch()

    def editSearch(self):
        toolTipTypes = {
            "main": [
                scroll.Line(
                    [
                        "<-- Line %i/%i -- >",
                        "(a) add, (e) select, (d) delete, or (q) quit",
                    ],
                    [0, "max-45"],
                    curses.COLS,
                )
            ],
            "press": [
                scroll.Line(
                    [
                        "Enter a subreddit number (1-%i), then press enter:",
                        "(press q to exit)",
                    ],
                    [0, "max-18"],
                    curses.COLS,
                )
            ],
            "enter": [
                scroll.Line(
                    [
                        "Enter a subreddit number (1-%i), then press enter:",
                        "(enter q to exit)",
                    ],
                    [0, "max-18"],
                    curses.COLS,
                )
            ],
            "input": [
                scroll.Line(
                    ["Enter name of subreddit, then press enter:", "(enter q to exit)"],
                    [0, "max-18"],
                    curses.COLS,
                )
            ],
        }
        toolTip = scroll.ToolTip(toolTipTypes["main"])
        scrollingList = scroll.ScrollingList(
            self.screen, self.viewSearchTree(self.search), tooltip=toolTip
        )

        page = p.Page(
            screen=self.screen,
            scrollingList=scrollingList,
            tooltip=toolTip,
            tooltipTypes=toolTipTypes,
            onUpdate=self.viewSearchTree,
            content=self.search,
            minRows=self.minLines,
            minCols=self.minCols,
        )
        page.switchTooltip("main")

        while True:
            # Updates the tooltip, and prints the headers to the screen
            page.refreshTooltip(
                "main", [page.currentLine() + 1, scrollingList.maxLine + 1], print=True
            )

            # Gets input from the user

            input = functions.eventListener(
                self.screen,
                bindings=[kb.controlKeys, kb.scrollVerticalKeys, kb.editKeys],
            )
            resized = False

            match input:
                case "timeout":
                    continue
                case "exit":
                    return resized
                case "enter":
                    if (
                        self.search.subreddits is not None
                        and len(self.search.subreddits) > 0
                    ):
                        # Updates the tooltip and places the cursor for input
                        page.refreshTooltip(
                            "press", (len(self.search.subreddits)), print=True
                        )

                        functions.placeCursor(self.screen, x=51, y=curses.LINES - 1)
                        c = self.screen.getch()  # Gets the character they type
                        if c == ord("q"):  # Immediately exits if they pressed q
                            continue

                        else:  # Otherwise
                            # Update prompt to tell them to 'enter q" instead of 'press q"
                            page.refreshTooltip(
                                "enter", (len(self.search.subreddits)), print=True
                            )
                            string = functions.getInput(
                                screen=self.screen, unget=c, col=51
                            )

                            # Attempts to convert their input into an integer.
                            val = 0
                            try:
                                val = int(string) - 1
                            except ValueError:
                                continue

                            # Checks if it is within the bounds of post numbersS
                            if val >= 0 and val < len(self.search.subreddits):
                                changes = self.editSubreddit(val)
                                if changes["resized"]:
                                    page.resize()
                                    resized = True
                                if changes["updated"]:
                                    if not changes["resized"]:
                                        page.updateContent()

                case "add":
                    page.refreshTooltip("input", print=True)
                    name = functions.getInput(self.screen, col=43)
                    self.search.addSub(search.SubredditSearch(name))
                    page.updateContent()
                case "delete":
                    if (
                        self.search.subreddits is not None
                        and len(self.search.subreddits) > 0
                    ):
                        # Updates the tooltip and places the cursor for input
                        page.refreshTooltip(
                            "press", (len(self.search.subreddits)), print=True
                        )

                        functions.placeCursor(self.screen, x=51, y=curses.LINES - 1)
                        c = self.screen.getch()  # Gets the character they type
                        if c == ord("q"):  # Immediately exits if they pressed q
                            continue
                        else:
                            # Update prompt to tell them to "enter q" instead of "press q"
                            page.refreshTooltip(
                                "enter", (len(self.search.subreddits)), print=True
                            )
                            string = functions.getInput(
                                screen=self.screen, unget=c, col=51
                            )

                            # Attempts to convert their input into an integer.
                            val = 0
                            try:
                                val = int(string) - 1
                            except ValueError:
                                continue

                            if val >= 0 and val < len(self.search.subreddits):
                                del self.search.subreddits[val]
                                page.updateContent()

                case _:
                    page.manipulate(input)

    def editSubreddit(self, index):
        self.subreddit = self.search.subreddits[index]
        toolTipTypes = {
            "main": [
                scroll.Line(
                    ["<-- Line %i/%i -- >", "(press e to select a filter to edit)"],
                    [0, "max-37"],
                    curses.COLS,
                )
            ],
            "press": [
                scroll.Line(
                    [
                        "Enter a filter number (1-%i), then press enter:",
                        "(press q to exit)",
                    ],
                    [0, "max-18"],
                    curses.COLS,
                )
            ],
            "enter": [
                scroll.Line(
                    [
                        "Enter a filter number (1-%i), then press enter:",
                        "(enter q to exit)",
                    ],
                    [0, "max-18"],
                    curses.COLS,
                )
            ],
        }
        toolTip = scroll.ToolTip(toolTipTypes["main"])
        scrollingList = scroll.ScrollingList(
            self.screen,
            self.viewSubTree(self.search.subreddits[index]),
            tooltip=toolTip,
        )

        page = p.Page(
            screen=self.screen,
            scrollingList=scrollingList,
            tooltip=toolTip,
            tooltipTypes=toolTipTypes,
            onUpdate=self.viewSubTree,
            content=self.search.subreddits[index],
            minRows=self.minLines,
            minCols=self.minCols,
        )
        page.switchTooltip("main")

        resized = False
        updated = False

        while True:
            # Updates the tooltip, and prints the headers to the screen
            page.refreshTooltip(
                "main", [page.currentLine() + 1, scrollingList.maxLine + 1], print=True
            )

            # Gets input from the user

            filterInput = functions.eventListener(
                self.screen, bindings=[kb.controlKeys, kb.editKeys]
            )

            match filterInput:
                case "timeout":
                    continue
                case "exit":
                    return {"resized": resized, "updated": updated}
                case "enter":
                    # Updates the tooltip and places the cursor for input
                    page.refreshTooltip("press", (6), print=True)

                    functions.placeCursor(self.screen, x=48, y=curses.LINES - 1)
                    c = self.screen.getch()  # Gets the character they type
                    if c == ord("q"):  # Immediately exits if they pressed q
                        continue

                    else:  # Otherwise
                        # Update prompt to tell them to 'enter q" instead of 'press q"
                        page.refreshTooltip("enter", (6), print=True)
                        string = functions.getInput(
                            screen=self.screen,
                            page=scrollingList,
                            tooltip=toolTip,
                            unget=c,
                            col=48,
                        )

                        # Attempts to convert their input into an integer.
                        val = 0
                        try:
                            val = int(string) - 1
                        except ValueError:
                            continue

                        # Checks if it is within the bounds of post numbersS
                        if val >= 0 and val < 6:
                            changes = self.editFilter(index, val)
                            if changes["resized"]:
                                resized = True
                                page.resize()
                            if changes["updated"]:
                                updated = True
                                if not changes["resized"]:
                                    page.updateContent()

                case _:
                    if page.manipulate(filterInput) == 1:
                        resized = True

    def editFilter(self, index, filterValue):
        toolTipTypes = {
            "main": [
                scroll.Line(
                    ["<-- Line %i/%i -- >", "(a) add, (d) delete, or (q) quit"],
                    [0, "max-33"],
                    curses.COLS,
                )
            ],
            "press": [
                scroll.Line(
                    [
                        "Enter a filter number (1-%i), then press enter:",
                        "(press q to exit)",
                    ],
                    [0, "max-18"],
                    curses.COLS,
                )
            ],
            "enter": [
                scroll.Line(
                    [
                        "Enter a filter number (1-%i), then press enter:",
                        "(enter q to exit)",
                    ],
                    [0, "max-18"],
                    curses.COLS,
                )
            ],
            "input": [
                scroll.Line(
                    ["Enter the filter, then press enter:"],
                    [0],
                    curses.COLS,
                )
            ],
        }
        toolTip = scroll.ToolTip(toolTipTypes["main"])
        scrollingList = scroll.ScrollingList(self.screen, "", tooltip=toolTip)
        page = p.Page()
        content = None
        match filterValue:
            case 0:
                content = self.subreddit.titleWL
                page.update(
                    screen=self.screen,
                    scrollingList=scrollingList,
                    tooltip=toolTip,
                    tooltipTypes=toolTipTypes,
                    onUpdate=self.treeWT,
                    content=content,
                    minRows=self.minLines,
                    minCols=self.minCols,
                )
            case 1:
                content = self.subreddit.titleBL
                page.update(
                    screen=self.screen,
                    scrollingList=scrollingList,
                    tooltip=toolTip,
                    tooltipTypes=toolTipTypes,
                    onUpdate=self.treeBT,
                    content=content,
                    minRows=self.minLines,
                    minCols=self.minCols,
                )
            case 2:
                content = self.subreddit.flairWL
                page.update(
                    screen=self.screen,
                    scrollingList=scrollingList,
                    tooltip=toolTip,
                    tooltipTypes=toolTipTypes,
                    onUpdate=self.treeWF,
                    content=content,
                    minRows=self.minLines,
                    minCols=self.minCols,
                )
            case 3:
                content = self.subreddit.flairBL
                page.update(
                    screen=self.screen,
                    scrollingList=scrollingList,
                    tooltip=toolTip,
                    tooltipTypes=toolTipTypes,
                    onUpdate=self.treeBF,
                    content=content,
                    minRows=self.minLines,
                    minCols=self.minCols,
                )
            case 4:
                content = self.subreddit.postWL
                page.update(
                    screen=self.screen,
                    scrollingList=scrollingList,
                    tooltip=toolTip,
                    tooltipTypes=toolTipTypes,
                    onUpdate=self.treeWP,
                    content=content,
                    minRows=self.minLines,
                    minCols=self.minCols,
                )
            case 5:
                content = self.subreddit.postBL
                page.update(
                    screen=self.screen,
                    scrollingList=scrollingList,
                    tooltip=toolTip,
                    tooltipTypes=toolTipTypes,
                    onUpdate=self.treeBP,
                    content=content,
                    minRows=self.minLines,
                    minCols=self.minCols,
                )
            case _:
                return False
        page.updateContent(content)
        page.switchTooltip("main")
        resized = False
        updated = False

        while True:
            # Updates the tooltip, and prints the headers to the screen
            page.refreshTooltip(
                "main", [page.currentLine() + 1, scrollingList.maxLine + 1], print=True
            )

            # Gets input from the user

            input = functions.eventListener(
                self.screen, bindings=[kb.controlKeys, kb.editKeys]
            )

            match input:
                case "timeout":
                    continue
                case "exit":
                    return {"resized": resized, "updated": updated}
                case "add":
                    page.refreshTooltip("input", print=True)
                    name = functions.getInput(self.screen, col=36)
                    match filterValue:
                        case 0:
                            self.subreddit.add(titleWL=name)
                            content = self.subreddit.titleWL
                        case 1:
                            self.subreddit.add(titleBL=name)
                            content = self.subreddit.titleBL
                        case 2:
                            self.subreddit.add(flairWL=name)
                            content = self.subreddit.flairWL
                        case 3:
                            self.subreddit.add(flairBL=name)
                            content = self.subreddit.flairBL
                        case 4:
                            self.subreddit.add(postWL=name)
                            content = self.subreddit.postWL
                        case 5:
                            self.subreddit.add(postBL=name)
                            content = self.subreddit.postBL
                    page.updateContent(content)
                    updated = True

                    match filterValue:
                        case 0:
                            pass
                case "delete":
                    # Updates the tooltip and places the cursor for input
                    match filterValue:
                        case 0:
                            if self.subreddit.titleWL is not None:
                                page.refreshTooltip(
                                    "press", len(self.subreddit.titleWL), print=True
                                )
                            else:
                                continue
                        case 1:
                            if self.subreddit.titleBL is not None:
                                page.refreshTooltip(
                                    "press", len(self.subreddit.titleBL), print=True
                                )
                            else:
                                continue
                        case 2:
                            if self.subreddit.flairWL is not None:
                                page.refreshTooltip(
                                    "press", len(self.subreddit.flairWL), print=True
                                )
                            else:
                                continue
                        case 3:
                            if self.subreddit.flairBL is not None:
                                page.refreshTooltip(
                                    "press", len(self.subreddit.flairBL), print=True
                                )
                            else:
                                continue
                        case 4:
                            if self.subreddit.postWL is not None:
                                page.refreshTooltip(
                                    "press", len(self.subreddit.postWL), print=True
                                )
                            else:
                                continue
                        case 5:
                            if self.subreddit.postBL is not None:
                                page.refreshTooltip(
                                    "press", len(self.subreddit.postBL), print=True
                                )
                            else:
                                continue

                    functions.placeCursor(self.screen, x=48, y=curses.LINES - 1)
                    c = self.screen.getch()  # Gets the character they type
                    if c == ord("q"):  # Immediately exits if they pressed q
                        continue

                    else:  # Otherwise
                        # Update prompt to tell them to 'enter q" instead of 'press q"
                        match filterValue:
                            case 0:
                                if self.subreddit.titleWL is not None:
                                    page.refreshTooltip(
                                        "enter", len(self.subreddit.titleWL), print=True
                                    )
                                else:
                                    continue
                            case 1:
                                if self.subreddit.titleBL is not None:
                                    page.refreshTooltip(
                                        "enter", len(self.subreddit.titleBL), print=True
                                    )
                                else:
                                    continue
                            case 2:
                                if self.subreddit.flairWL is not None:
                                    page.refreshTooltip(
                                        "enter", len(self.subreddit.flairWL), print=True
                                    )
                                else:
                                    continue
                            case 3:
                                if self.subreddit.flairBL is not None:
                                    page.refreshTooltip(
                                        "enter", len(self.subreddit.flairBL), print=True
                                    )
                                else:
                                    continue
                            case 4:
                                if self.subreddit.postWL is not None:
                                    page.refreshTooltip(
                                        "enter", len(self.subreddit.postWL), print=True
                                    )
                                else:
                                    continue
                            case 5:
                                if self.subreddit.postBL is not None:
                                    page.refreshTooltip(
                                        "enter", len(self.subreddit.postBL), print=True
                                    )
                                else:
                                    continue

                        string = functions.getInput(screen=self.screen, unget=c, col=48)

                        # Attempts to convert their input into an integer.
                        val = 0
                        try:
                            val = int(string) - 1
                        except ValueError:
                            continue

                        # Checks if it is within the bounds of post numbers
                        match filterValue:
                            case 0:
                                if val >= 0 and val < len(self.subreddit.titleWL):
                                    del self.subreddit.titleWL[val]
                            case 1:
                                if val >= 0 and val < len(self.subreddit.titleBL):
                                    del self.subreddit.titleBL[val]
                            case 2:
                                if val >= 0 and val < len(self.subreddit.flairWL):
                                    del self.subreddit.flairWL[val]
                            case 3:
                                if val >= 0 and val < len(self.subreddit.flairBL):
                                    del self.subreddit.flairBL[val]
                            case 4:
                                if val >= 0 and val < len(self.subreddit.postWL):
                                    del self.subreddit.postWL[val]
                            case 5:
                                if val >= 0 and val < len(self.subreddit.postBL):
                                    del self.subreddit.postBL[val]

                        page.updateContent()

                case _:
                    if page.manipulate(input) == 1:
                        resized = True

    def viewSearchTree(self, search):
        return tree.searchTree(
            search, curses.COLS, config.fancy_characters, enumerate=True
        )

    def viewSubTree(self, subreddit):
        return tree.subTree(subreddit, curses.COLS, config.fancy_characters)

    def treeWT(self, filterContent):
        return tree.filterTree(
            self.subreddit.name,
            "Title whitelist",
            filterContent,
            curses.COLS,
            config.fancy_characters,
            True,
        )

    def treeBT(self, filterContent):
        return tree.filterTree(
            self.subreddit.name,
            "Title blacklist",
            filterContent,
            curses.COLS,
            config.fancy_characters,
            True,
        )

    def treeWF(self, filterContent):
        return tree.filterTree(
            self.subreddit.name,
            "Flair whitelist",
            filterContent,
            curses.COLS,
            config.fancy_characters,
            True,
        )

    def treeBF(self, filterContent):
        return tree.filterTree(
            self.subreddit.name,
            "Flair blacklist",
            filterContent,
            curses.COLS,
            config.fancy_characters,
            True,
        )

    def treeWP(self, filterContent):
        return tree.filterTree(
            self.subreddit.name,
            "Post whitelist",
            filterContent,
            curses.COLS,
            config.fancy_characters,
            True,
        )

    def treeBP(self, filterContent):
        return tree.filterTree(
            self.subreddit.name,
            "Post blacklist",
            filterContent,
            curses.COLS,
            config.fancy_characters,
            True,
        )
