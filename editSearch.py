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
                            changes = self.editFilter(filterValue = val)
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

    def editFilter(self, filterValue):
        match filterValue:
            case 0:
                return self.editFilterIndividual(self.subreddit.titleWL)
            case 1:
                return self.editFilterIndividual(self.subreddit.titleBL)
            case 2:
                return self.editFilterIndividual(self.subreddit.flairWL)
            case 3:
                return self.editFilterIndividual(self.subreddit.flairBL)
            case 4:
                return self.editFilterIndividual(self.subreddit.postWL)
            case 5:
                return self.editFilterIndividual(self.subreddit.postBL)
            case _:
                return False

    
    def editFilterIndividual(self, filter):
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
        onUpdate = None
        page.update(
            screen=self.screen,
            scrollingList=scrollingList,
            tooltip=toolTip,
            tooltipTypes=toolTipTypes,
            onUpdate=onUpdate,
            content=content,
            minRows=self.minLines,
            minCols=self.minCols,
        )
        content = filter
        onUpdate = self.filterUpdate
        
        page.update_onUpdate(onUpdate)
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
                    filter.add(name)
                    content = filter
                    
                    page.updateContent(content)
                    updated = True

                    
                case "delete":
                    # Updates the tooltip and places the cursor for input
                    if filter is not None:
                        page.refreshTooltip(
                            "press", len(filter.content), print=True
                        )
                    else:
                        continue
                    

                    functions.placeCursor(self.screen, x=48, y=curses.LINES - 1)
                    c = self.screen.getch()  # Gets the character they type
                    if c == ord("q"):  # Immediately exits if they pressed q
                        continue

                    else:  # Otherwise
                        # Update prompt to tell them to 'enter q" instead of 'press q"
                        if filter is not None:
                            page.refreshTooltip(
                                "enter", len(filter.content), print=True
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
                        if val >= 0 and val < len(filter.content):
                            del filter.content[val]
                            updated = True

                        page.updateContent()

                case _:
                    if page.manipulate(input) == 1:
                        resized = True
            
        
    
    
    def viewSearchTree(self, search):
        search.tree.cascading_update(set_fancy=config.fancy_characters)
        return search.tree.print(as_a_string=False)


    def viewSubTree(self, subreddit):
        subreddit.tree.cascading_update(set_fancy=config.fancy_characters)
        return subreddit.tree.print(as_a_string=False)

    def filterUpdate(self,filter):
        filter.tree.cascading_update(set_fancy=config.fancy_characters)
        return filter.tree.print(as_a_string=False)
    