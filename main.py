# Libraries
import praw
import prawcore
import curses
import math
import argparse
import sys
import json.decoder

# Provided files
import functions
import config
import dump
import constants
import formatString


parser = argparse.ArgumentParser(
    description="Gathers posts on Reddit that meets specific criteria. Note that the program can be run without any command-line options."
)
parser.add_argument(
    "-n",
    "--name",
    metavar="NAME",
    help="Name of the search to be performed. Case-sensitive.",
)
parser.add_argument(
    "-y",
    "--yes",
    action="store_true",
    help="Automatically agrees to prompts for confirmation.",
)
parser.add_argument(
    "-d",
    "--dontSave",
    action="store_true",
    help="Disables updating of last search time, leaving it how it was before performing the search.",
)
args = vars(parser.parse_args())

# Checks that the config options are set
if config.client_id == "":
    print("Please specify a client id in config.py")
    sys.exit(1)
if config.client_secret == "":
    print("Please specify a client secret in config.py")
    sys.exit(1)
if config.user_agent == "":
    print("Please specify a user agent in config.py")
    sys.exit(1)


# Read-only instance
reddit_read_only = praw.Reddit(
    client_id=config.client_id,  # your client id
    client_secret=config.client_secret,  # your client secret
    user_agent=config.user_agent,
)  # your user agent

# Pulls a post to test that config options are properly set
if config.praw_check:
    try:
        for post in reddit_read_only.subreddit("reddit").new(limit=1):
            post = post
    except prawcore.exceptions.ResponseException:
        print("Bad HTTP Response")
        print(
            "Please check that the client id, secret, and user agent are properly configured in config.py"
        )
        sys.exit(1)


# Ensures that the path to the searches file has been set
searchesPath = config.searches_file
if searchesPath == "":
    print("Please specify a path to the searches file in config.py")
    sys.exit(1)

# Initialization work
screen = curses.initscr()
curses.noecho()  # Does not display what user types
curses.cbreak()  # User does not have to press enter for the input buffer to be read
screen.keypad(True)  # Converts keys like arrow keys to a specific value

# Ensures the terminal is large enough to properly display (Can probably be changed in the future to be smaller)
minTermLines = 24
minTermCols = 80
if config.term_size_check:
    if curses.LINES < minTermLines or curses.COLS < minTermCols:
        # curses.nocbreak(); screen.keypad(0); curses.echo()
        # curses.endwin()
        functions.close(screen)
        print(
            f"The current terminal size {curses.LINES}x{curses.COLS} is too small. The minimum size supported is {minTermLines}x{minTermCols}"
        )
        sys.exit()

searches = []
try:
    searches = functions.getSearches(searchesPath)
except (FileNotFoundError, json.decoder.JSONDecodeError):
    searches = []

numPosts = 0  # Number of posts found meeting criteria
postNum = 0  # Number of the post to be viewed in full
lineNum = 0  # Current line number for paginating through post browsing
browseMode = True  # True if browsing through posts, false if reading a specific post
choosingSearches = True  # True if the user has yet to choose a search to perform, false if the search has been chosen
searchIndex = 0  # Index of the search to be performed
posts = []  # List of all the posts meeting criteria

"""
page = scroll.ScrollingList(screen, [""])
toolTipType = "main"
toolTipTypes = {
    "main": [
        scroll.Line(
            ["<-- Line %i/%i -- >", "(press e to view a post or q to quit)"],
            [0, "max-38"],
            curses.COLS,
        )
    ],
    "press": [
        scroll.Line(
            ["Enter a post number (1-%i), then press enter:", "(press q to exit)"],
            [0, "max-18"],
            curses.COLS,
        )
    ],
    "enter": [
        scroll.Line(
            ["Enter a post number (1-%i), then press enter:", "(enter q to exit)"],
            [0, "max-18"],
            curses.COLS,
        )
    ],
}
toolTip = scroll.ToolTip(toolTipTypes[toolTipType])

browsePage = p.Page(screen=screen,scrollingList=page,tooltip=toolTip,tooltipTypes=toolTipTypes,onUpdate=functions.getHeaders,minRows=minTermLines,minCols=minTermCols)
browsePage.switchTooltip("main")
"""

try:
    while True:
        screen.clear()

        # If the user still has to choose a search to perform
        if choosingSearches:
            # If searches were found in the search file
            if searches:
                if args["name"]:
                    valid = False
                    for item in range(len(searches)):
                        if searches[item].name == args["name"]:
                            valid = True
                            searchIndex = item
                            break
                    if not valid:  # Closes window, then prints out all valid searches found in the file, and finally exits
                        functions.close(screen)
                        print(
                            f"No search by the name of '{args['name']}' exists\nThe following are valid searches:"
                        )
                        for item in searches:
                            print(f"\t{item.name}")
                        print("", flush=True)
                        sys.exit(1)

                else:
                    searchIndex = functions.getSearchNum(screen, searches)
            else:  # If no searches were found in the file, or the file does not exist
                screen.addstr(0, 0, "No searches found at the current searches file:")
                screen.addstr(1, 0, f">   {searchesPath}")
                screen.addstr(
                    2,
                    0,
                    "If this is not the correct path, edit the value of 'searches_file' in config.py.",
                )
                screen.addstr(3, 0, "Press q to quit the program.")
                screen.addstr(
                    4,
                    0,
                    "Press any other key to create a new search in the above search file",
                )
                char = screen.getch()
                if char == ord("q"):
                    break
                else:
                    searchIndex = -2

            screen.clear()
            screen.refresh()
            # If the user indicated that they wanted to quit the program in getSearchNum
            if searchIndex == -1:
                break
            elif searchIndex == -2:
                newSearch = functions.createSearch(screen)
                if newSearch is not None:
                    searches.append(newSearch)
                    dump.saveSearches(searches, searchesPath)
                continue
            elif searchIndex == -3:
                dump.saveSearches(searches, searchesPath)
                continue

            else:
                choosingSearches = False
                currentTime = functions.currentTimestamp()
                searchTime = (
                    searches[searchIndex].lastSearchTime
                )  # Gets the last time the specified search was performed

            # If search has never been performed
            if searchTime is None or searchTime == 0:
                screen.clear()
                if not args["yes"]:
                    screen.addstr(
                        0,
                        0,
                        "This search has never been performed. Gathering posts from the last week.",
                    )
                    screen.addstr(1, 0, "Press q to quit or any other key to continue")
                    screen.refresh()
                    char = screen.getch()
                    if char == ord("q"):
                        break
                searches[searchIndex].lastSearchTime = math.floor(
                    functions.currentTimestamp() - constants.DAY * 7
                )

            # If search was last performed over a week ago
            elif currentTime - searchTime > constants.DAY * 7:
                screen.clear()
                char = "y"
                if not args["yes"]:
                    screen.addstr(
                        0,
                        0,
                        f"This search was last performed {formatString.formatAge(currentTime-searchTime,'ago.')}",
                    )
                    screen.addstr(1, 0, "Press q to quit,")
                    screen.addstr(2, 0, "y to perform the search anyways,")
                    screen.addstr(
                        3, 0, "or n to perform search on posts from the last week"
                    )
                    screen.refresh()

                    char = screen.getch()
                if char == ord("q"):
                    break
                elif not char == ord("y"):
                    searches[searchIndex].lastSearchTime = math.floor(
                        functions.currentTimestamp() - constants.DAY * 7
                    )

            # Records the current timestamp before performing the search, then performs the search
            time = math.floor(functions.currentTimestamp())
            for sub in searches[searchIndex].subreddits:
                status = functions.isValidSubreddit(reddit_read_only, sub.name)
                if status == -1:
                    functions.close(screen)

                    print(
                        f"Subreddit ({sub.name}) does not exist or has been banned",
                        flush=True,
                    )
                    sys.exit(1)
                elif status == -2:
                    functions.close(screen)
                    print(
                        f"Subreddit ({sub.name}) is private or under quarantine",
                        flush=True,
                    )
                    sys.exit(1)

            posts = posts + functions.completeSearch(
                reddit_read_only,
                searches,
                searchIndex,
                posts,
                screen,
                minTermCols,
                minTermLines,
                not args["dontSave"],
                searchesPath,
            )

            numPosts = len(posts)

            # If no posts matched the criteria
            if numPosts <= 0:
                screen.clear()
                screen.addstr(0, 0, "No posts found")
                screen.addstr(curses.LINES - 1, 0, "Press any key to exit")
                screen.getch()
                screen.refresh()
                break

            # If at least one post matching the criteria was found
            else:
                # browsePage.updateContent(posts)
                pass

            # Clears screen after search choosing process
            screen.clear()
            screen.refresh()

        # Displays a single post
        elif not browseMode:
            next = functions.viewPost(posts[postNum], screen, minTermCols, minTermLines)
            if next == -1:  # The user wants to view previous post
                if postNum > 0:
                    postNum = postNum - 1
            elif next == 1:  # The user wants to view next post
                if (postNum + 1) < len(posts):
                    postNum = postNum + 1
            else:  # User wanted to exit viewPost
                browseMode = True

        # Displays post headers for browsing
        else:
            postNum = functions.browsePosts(posts, screen, minTermCols, minTermLines)

            if postNum == -1:  # User wanted to exit browsePosts
                if args["name"]:
                    break
                else:
                    choosingSearches = True
            elif postNum == -2:  # User refreshed posts
                posts = functions.completeSearch(
                    reddit_read_only,
                    searches,
                    searchIndex,
                    posts,
                    screen,
                    minTermCols,
                    minTermLines,
                    not args["dontSave"],
                    searchesPath,
                )
                # browsePage.updateContent(posts)
                numPosts = len(posts)
            else:  # User selected a post to view
                browseMode = False


# Resets the terminal window for normal usage outside of the program
finally:
    functions.close(screen)
