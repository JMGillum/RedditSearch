import constants
# import math


def removeNonAscii(text):
    """
    Keeps only the first 256 characters of extended ASCII. Probably bad for portability
    """
    newString = ""
    for char in text:
        if ord(char) <= 255:
            newString = newString + char
    return newString


def formatAge(age, suffix=""):
    """
    Takes a time (age) in seconds, and returns a string that describes it with the largest unit that
    is smaller than the time. ex: age = 119, returns 'one minute', age = 95000, returns 'one day.'
    Suffix is used to append some phrase after the unit, such as 'ago.' The suffix is not applied to the
    just now unit (ages less than 60 seconds)
    """

    try:
        age + 1
    except TypeError:
        return f"{age}"

    ticker = 0

    if age > constants.YEAR:  # Years
        while age > constants.YEAR:
            age -= constants.YEAR
            ticker += 1
        if ticker > 1:
            return f"{ticker} years {suffix}"
        else:
            return f"{ticker} year {suffix}"

    elif age > constants.MONTH:  # Months
        while age > constants.MONTH:
            age -= constants.MONTH
            ticker += 1
        if ticker > 1:
            return f"{ticker} months {suffix}"
        else:
            return f"{ticker} month {suffix}"

    elif age > constants.DAY:  # Days
        while age > constants.DAY:
            age -= constants.DAY
            ticker += 1
        if ticker > 1:
            return f"{ticker} days {suffix}"
        else:
            return f"{ticker} day {suffix}"

    elif age > constants.HOUR:  # Hours
        while age > constants.HOUR:
            age -= constants.HOUR
            ticker += 1
        if ticker > 1:
            return f"{ticker} hours {suffix}"
        else:
            return f"{ticker} hour {suffix}"

    elif age > constants.MINUTE:  # Minutes
        while age > constants.MINUTE:
            age -= constants.MINUTE
            ticker += 1
        if ticker > 1:
            return f"{ticker} minutes {suffix}"
        else:
            return f"{ticker} minute {suffix}"

    else:  # Times less than 60 seconds (1 minute)
        return "just now"


def placeString(string, length, start=0):
    """
    Places string at location start, and fills with spaces (at the end) until it is size length
    """
    if len(string) >= length:
        return string
    s = spacesString(length)
    s = s[:start] + string + s[start + len(string) :]
    return s


def combineStrings(stringA, stringB, length, startA, startB):
    if startB < startA:
        return combineStrings(stringB, stringA, length, startB, startA)
    stringA = placeString(stringA, length, startA)
    string = stringA[:startB] + stringB + stringA[startB + len(stringB) :]
    return string


def spacesString(spaces):
    """
    Returns a string of spaces, with length equal to spaces parameter
    """
    return "".zfill(spaces).replace("0", " ")


def tabulate(string, terminalWidth=80, spaces=8):
    """
    Given a string, splits the string across enough lines, such that there
    each line begins with spaces number of spaces, and the total length of the line
    does not exceed terminalWidth. Each line is terminated with '\n'
    """
    # Removes tabs from the original string
    string = string.replace("\t", "")

    # Splits the string into a list, separating at newlines already present (ends of paragraphs)
    stringList = string.splitlines()

    offset = terminalWidth - spaces  # the number of non-space characters for the line
    tempstr = ""  # Stores the working string while it is being built up
    checkstr = ""  # Used for checking if adding the next word will push the string over the length limit
    tabulatedList = []  # A list comprised of each finished line
    for item in stringList:
        item = (
            item.split()
        )  # Splits the paragraphs up by words. Separating at every space
        for word in item:  # Loops through every word
            # If the word is longer than the amount of space for a single line
            if len(word) > offset:
                # Finishes the work in progress line
                tabulatedList.append(f"{spacesString(spaces)}{checkstr}\n")
                tempstr = ""
                checkstr = ""

                # Used to split the long word (typically links) into multiple lines
                workingWord = word

                # Splits word into offset sized lines
                while len(workingWord) > offset:
                    tabulatedList.append(
                        f"{spacesString(spaces)}{workingWord[:offset]}\n"
                    )
                    workingWord = workingWord[offset:]

                # Gives the end of the word (the part less than offset length) its own line
                tabulatedList.append(f"{spacesString(spaces)}{workingWord}\n")
                continue

            # For normal words
            checkstr = checkstr + word
            if (
                len(checkstr) < offset
            ):  # simply adds new word to tempstr if it won't make it too long
                tempstr = checkstr
                tempstr = tempstr + " "
                checkstr = tempstr
            elif (
                len(checkstr) == offset
            ):  # Adds word, then pushes line to list and starts new line
                tabulatedList.append(f"{spacesString(spaces)}{checkstr}\n")
                tempstr = ""
                checkstr = ""
            else:  # Pushes current line to list, then starts a new line with word at the start
                tabulatedList.append(f"{spacesString(spaces)}{tempstr}\n")
                tempstr = word + " "
                checkstr = tempstr

        # Adds leftover words at the end of paragraph
        tabulatedList.append(f"{spacesString(spaces)}{tempstr}\n")
        tempstr = ""
        checkstr = ""

    newStr = ""
    return newStr.join(tabulatedList)  # Combines list into a single string


def enbox(
    stringList,
    terminalWidth,
    leftPadding=1,
    rightPadding=1,
    leftMargin=0,
    rightMargin=0,
    fancy=False,
):
    """
    Draws boxes around content. stringList is a list of strings of content. All entries in the list will be combined
    into the same box. Using "%separator%" as an entry in the list will draw a horizontal line. terminalWidth is the width of the box.
    Padding is the number of spaces between side walls and content.
    Margin is the number of spaces between the edge of terminal and the side walls.
    fancy is whether fancy characters will be used or basic characters.
    """
    boxWidth = terminalWidth - (leftMargin + rightMargin)
    textBoxWidth = boxWidth - (leftPadding + rightPadding)

    topLeft = "+"
    topRight = "+"
    bottomLeft = "+"
    bottomRight = "+"
    sideLeft = "+"
    sideRight = "+"
    vertical = "|"
    horizontal = "-"

    if fancy:
        topLeft = "┌"
        topRight = "┐"
        bottomLeft = "└"
        bottomRight = "┘"
        sideLeft = "├"
        sideRight = "┤"
        vertical = "│"
        horizontal = "─"

    s = []

    # Creates the top border of the box
    s.append(f"{topLeft}{''.zfill(boxWidth-2).replace('0',horizontal)}{topRight}")

    for item in stringList:  # Loops through each item in the content list.
        if item is not None:
            # Creates a separating line in the box
            if item == "%separator%":
                # Adds a horizontal line
                s.append(
                    f"{sideLeft}{''.zfill(boxWidth-2).replace('0',horizontal)}{sideRight}"
                )
            else:
                # Breaks the content into lines that will fit in the text box.
                listStrings = tabulate(item, textBoxWidth - 1, leftPadding).splitlines()
                for line in listStrings:
                    # Adds the side walls and appends the line to the list of lines
                    line = placeString(line, textBoxWidth, 0)
                    s.append(f"{vertical}{line}{vertical}")

    # Creates bottom line
    s.append(f"{bottomLeft}{''.zfill(boxWidth-2).replace('0',horizontal)}{bottomRight}")
    return s
