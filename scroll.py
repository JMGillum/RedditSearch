import curses

from formatString import combineStrings


class ScrollingList:
    """
    Represents a list that can be scrolled through. Useful for displaying a large amount of related data.
    Requires a list of strings, a curses window object, and optionally a starting line number and/or a
    ToolTip object.
    """

    def __init__(self, screen, stringList, line=0, tooltip=None):
        self.updateStrings(screen, stringList, line, tooltip)

    def updateStrings(self, screen, stringList, line=0, tooltip=None):
        self.screen = screen
        self.lines = stringList
        self.currentLine = line
        self.updateTooltip(tooltip)

    def scrollDown(self, numLines=1):
        """
        Moves the lines that will be shown down by numLines.
        Returns the current line number
        """
        if (
            self.currentLine + numLines > self.maxLine
        ):  # Checks if scrolling down by numLines will scroll down to far
            self.currentLine = self.maxLine
        else:
            self.currentLine += numLines
        return self.currentLine

    def scrollBottom(self):
        """
        Scrolls to the bottom of the list and returns the current line number
        """
        self.currentLine = self.maxLine
        return self.currentLine

    def scrollUp(self, numLines=1):
        """
        Moves the lines that will be shown up by numLines and returns the current line number
        """
        if (
            self.currentLine - numLines < 0
        ):  # checks if scrolling up by numLines will scroll above the first line
            self.currentLine = 0
        else:
            self.currentLine = self.currentLine - numLines
        return self.currentLine

    def scrollTop(self):
        """
        Scrolls to the top of the list and returns the current line number
        """
        self.currentLine = 0
        return self.currentLine

    def getLines(self):
        """
        Returns a list of all the lines that can be fit in the terminal size - the size of the tooltip. Then appends
        the lines of the tooltip after these lines.
        """
        lines = []
        if self.tooltip is not None:  # Adds the lines of the tooltip if it exists
            numLines = (
                curses.LINES - self.tooltip.height()
            )  # Counts how many non-tooltip lines to get
            lines = self.lines[
                self.currentLine : self.currentLine + numLines
            ]  # numlines lines from currentline onward
            while (
                len(lines) < numLines
            ):  # if there aren't enough lines of content to fill the screen, add blank lines
                lines.append("")
            for item in self.tooltip.lines:  # Adds the lines of the tooltip
                lines = lines + [item.string]
            if (len(lines) == curses.LINES) and (
                len(lines[-1]) >= curses.COLS
            ):  # If the last line is equal to the length of the terminal,
                lines[-1] = lines[-1][
                    :-1
                ]  # Chops of the last character (otherwise curses would throw an error saying printing has happened outside of the terminal)
        else:  # Tooltip does not exist. Does samething as if it did exist, but prints content on all of the lines
            numLines = curses.LINES
            lines = self.lines[self.currentLine : self.currentLine + numLines]
            while len(lines) < numLines:
                lines.append("")
            if (len(lines) == curses.LINES) and (len(lines[-1]) >= curses.COLS):
                lines[-1] = lines[-1][:-1]
        return lines

    def updateTooltip(self, tooltip):
        """
        Replaces the tooltip
        """
        # Adjusts the number of lines of content that can be printed, based off of the number of lines in the tooltip
        self.maxLine = curses.LINES
        self.tooltip = None
        if tooltip is not None:
            self.tooltip = tooltip
            self.maxLine -= (
                self.tooltip.height()
            )  # Applies line adjustment for new tooltip

        if len(self.lines) >= self.maxLine:
            self.maxLine = len(self.lines) - self.maxLine
        else:
            self.maxLine = 0

    def print(self, numLines=None):
        """
        Prints the values returned by getLines to the screen. Prints numLines number of lines if specified
        """
        if numLines is None or numLines > 0:
            ticker = 0
            self.screen.clear()
            for item in self.getLines():
                self.screen.addstr(ticker, 0, f"{item}")
                ticker = ticker + 1
                if numLines is not None and ticker >= numLines:
                    self.screen.refresh()
                    break
            self.screen.refresh()


class ToolTip:
    """
    Represents the tooltip that is anchored to the bottom of a scrolling list. Items will be displayed
    in the order that they are added. Those added first will be above those added later
    """

    def __init__(self, lines):
        self.replace(lines)

    def replace(self, lines):
        """
        Replaces all of the lines of the tooltip with the new lines.
        """
        self.lines = []
        if isinstance(lines, str):  # Converts a string to a Line object
            self.lines.append(Line(lines, 0))
        elif isinstance(lines, list):
            for item in lines:
                if isinstance(item, str):  # Converts a string to a Line object
                    self.lines.append(Line(item, 0))
                elif isinstance(item, Line):
                    self.lines.append(item)
        self.resize()
        self.format = self.lines

    def update(self, lines, index=0):
        """
        Updates the lines starting at index with the lines specified
        """
        temp = self.lines
        try:
            lines = [lines]
            # Loops through each item in list, replacing elements in self.lines with them
            for item in lines:  # Starts at index, and replaces elements until the end of lines has been reached
                if isinstance(item, str):
                    self.lines[index] = Line(item, 0)
                elif isinstance(item, Line):
                    self.lines[index] = item
                index = index + 1
        except (
            IndexError
        ):  # If lines was too long, reset self.lines back to its original value
            self.lines = temp

        self.resize()
        self.format = self.lines

    def resize(self):
        for line in self.lines:
            line.resize()

    def updateVars(self, values, index=0):
        """
        Replaces %i in the lines starting at index with the values in values. The first %i encountered it replaced
        with the first value in values, the second with the second, and so on.
        """
        if values is not None:
            if index < len(self.lines):
                self.lines[index].updateVars(values)

    def height(self):
        """
        Returns the number of lines taken up by the tooltip
        """
        return len(self.lines)


class Line:
    """
    Represents a single line of content made out of sections that are anchored at specific locations
    """

    def __init__(self, sections, positions, length=80):
        self.string = ""
        self.sections = []
        self.positions = []
        self.length = 0
        self.format = []

        self.replace(sections, positions, length)

    def replace(self, sections, positions, length=80):
        """
        Replaces the content of the line
        """
        if sections is not None and positions is not None:
            if isinstance(sections, str):  # Converts sections to a list
                sections = [sections]
            if isinstance(
                sections, list
            ):  # Ensures that a list was passed by sectionis
                if isinstance(positions, int):  # Converts positions to a string
                    positions = [positions]
                if isinstance(positions, list):
                    if len(sections) == len(
                        positions
                    ):  # The length of sections and positions must be the same
                        self.sections = list(
                            sections
                        )  # Creates a separate list in memory to assign to self.sections
                        self.format = list(
                            sections
                        )  # Stores the content before its variables (%i) have been replaced
                        self.positions = positions
                        self.length = length
                        self.place()  # Combines all of the strings
                        self.previousValues = None

    def place(self):
        """
        Combines all of the strings at their specified locations
        """
        self.string = ""
        for index in range(len(self.sections)):
            if isinstance(self.positions[index], str):
                string = self.positions[index].lower()
                string.replace(" ", "")
                i = string.find("max")
                if i != -1:
                    try:
                        if string[i + 3] == "-":
                            try:
                                value = int(string[i + 4 :])
                                value = curses.COLS - value

                                if value < 0:
                                    continue
                                self.string = combineStrings(
                                    self.string,
                                    self.sections[index],
                                    self.length,
                                    0,
                                    value,
                                )
                            except AttributeError:
                                continue
                    except IndexError:
                        continue

            else:
                self.string = combineStrings(
                    self.string,
                    self.sections[index],
                    self.length,
                    0,
                    self.positions[index],
                )

    def resize(self):
        """
        Alternative name for Line.place(), but also adjusts Line.length to be the size of curses.COLS if necessary
        """
        if self.length != curses.COLS:
            self.length = curses.COLS
            self.place()

    def updateVars(self, values):
        """
        Replaces variables markers with values
        """
        # Only updates if the value of any variable has changed. Prevents updating to the same value, which would waste time.
        if values is not None and self.previousValues != values:
            lines = []
            valIndex = 0
            index = 0
            if not isinstance(values, list):
                values = [values]
            for section in range(len(self.format)):
                text = self.format[section]
                while True:
                    if valIndex >= len(values):
                        break
                    index = text.find("%i")
                    if index == -1:
                        break
                    text = f"{text[:index]}{values[valIndex]}{text[index+2:]}"
                    valIndex = valIndex + 1
                lines.append(text)
            self.sections = lines
            self.place()
            self.previousValues = values
