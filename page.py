import curses

from scroll import ScrollingList, ToolTip


class Page:
    def __init__(
        self,
        screen=None,
        scrollingList=None,
        tooltip=None,
        tooltipTypes=None,
        onUpdate=None,
        content=None,
        minRows=24,
        minCols=80,
    ):
        self.update(
            screen=screen,
            scrollingList=scrollingList,
            tooltip=tooltip,
            tooltipTypes=tooltipTypes,
            onUpdate=onUpdate,
            content=content,
            minRows=minRows,
            minCols=minCols,
        )

    def update(
        self,
        screen=None,
        scrollingList=None,
        tooltip=None,
        tooltipTypes=None,
        onUpdate=None,
        content=None,
        minRows=24,
        minCols=80,
    ):
        if isinstance(screen, curses.window):
            self.screen = screen
        else:
            self.screen = None

        if isinstance(scrollingList, ScrollingList):
            self.scrollingList = scrollingList
        else:
            self.scrollingList = None

        if isinstance(tooltip, ToolTip):
            self.tooltip = tooltip
        else:
            self.tooltip = None
        self.tooltipTypes = tooltipTypes
        self.tooltipType = None

        self.content = content
        self.onUpdate = onUpdate
        self.minRows = minRows
        self.minCols = minCols

    def updateContent(self, content=None):
        if content is not None:
            self.content = content
        self.scrollingList.updateStrings(
            self.screen,
            self.onUpdate(self.content),
            self.scrollingList.currentLine,
            self.tooltip,
        )

    def resize(self):
        if self.screen is not None:
            size = list(self.screen.getmaxyx())
            if size[0] < self.minRows:
                size[0] = self.minRows
            if size[1] < self.minCols:
                size[1] = self.minCols
            curses.resize_term(size[0], size[1])

        newContent = None
        if self.onUpdate is not None:
            newContent = self.onUpdate(self.content)  # Gets the properly sized content

        if self.scrollingList is not None:
            self.tooltip.resize()

            if newContent is not None:
                self.scrollingList.updateStrings(
                    self.screen,
                    newContent,
                    self.scrollingList.currentLine,
                    self.tooltip,
                )
            temp = self.scrollingList.currentLine
            lineNum = self.scrollingList.scrollDown()
            if not temp == lineNum:
                lineNum = self.scrollingList.scrollUp()

    def currentLine(self):
        """
        Returns the current line of the scrollingList object
        """
        if self.scrollingList is not None:
            return self.scrollingList.currentLine
        else:
            return -1

    def manipulate(self, method):
        if isinstance(method, str):
            match method:
                # Terminal was resized
                case "resize":
                    self.resize()
                    return 1

                # Scrolls up through the content list
                case "scrollUp":
                    self.scrollingList.scrollUp()
                    return 2

                # Scrolls to line 0 of the content
                case "scrollTop":
                    self.scrollingList.scrollTop()
                    return 3

                # Scrolls down through the content list
                case "scrollDown":
                    self.scrollingList.scrollDown()
                    return 4

                # Scrolls to the last line of the content list
                case "scrollBottom":
                    self.scrollingList.scrollBottom()
                    return 5

    def print(self, numLines=None):
        self.scrollingList.print(numLines)

    def switchTooltip(self, key):
        if self.tooltipType != key:
            try:
                text = self.tooltipTypes[key]
                self.tooltipType = key
                self.tooltip.replace(text)
            except KeyError:
                return

    def updateTooltip(self, vars, index=0):
        self.tooltip.updateVars(vars, index)

    def refreshTooltip(self, key, vars=None, index=0, print=False, numLines=None):
        self.switchTooltip(key)
        self.updateTooltip(vars, index)
        if print:
            self.print(numLines)
