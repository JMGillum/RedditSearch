# Used for setup and initialization process for program

import argparse
import curses
import prawcore

import config
import functions

def setupParser():
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
    return parser

def checkConfig():
    # Checks that the config options are set
    if config.client_id == "":
        print("Please specify a client id in config.py")
        return(False)
    if config.client_secret == "":
        print("Please specify a client secret in config.py")
        return(False)
    if config.user_agent == "":
        print("Please specify a user agent in config.py")
        return(False)
    return True

def checkPraw(redditObj):
    try:
        for post in redditObj.subreddit("reddit").new(limit=1):
            post = post
    except prawcore.exceptions.ResponseException:
        print("Bad HTTP Response")
        print(
            "Please check that the client id, secret, and user agent are properly configured in config.py"
        )
        return False
    return True


def checkCurses(lines,cols,screen):
    if curses.LINES < lines or curses.COLS < cols:
        # curses.nocbreak(); screen.keypad(0); curses.echo()
        # curses.endwin()
        functions.close(screen)
        print(
            f"The current terminal size {curses.LINES}x{curses.COLS} is too small. The minimum size supported is {lines}x{cols}"
        )
        return False
    return True