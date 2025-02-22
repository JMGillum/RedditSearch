# RedditSearch

[![asciicast](https://asciinema.org/a/Diol3laQUgbUkGypXuJ62v6Lo.svg)](https://asciinema.org/a/Diol3laQUgbUkGypXuJ62v6Lo)

Searches subreddits and filters by flair or title.

This program has only been tested on an Ubuntu-based Linux system. It should work on all Linux systems however.

Will only work on Python versions 3.12 and greater.
**Tested Python versions**: 3.12-3.13

**Table of Contents**:  

* [Installation](#installation)  
* [Usage](#usage)
  * [Creating a search](#creating-a-search)
    * [Filters](#filters)
    * [In app](#in-app)
    * [JSON](#json)
  * [Search Selection](#search-selection)
  * [Results](#results)
  * [Viewing a Post](#viewing-a-post)
    * [Navigation](#navigation)
    * [Interacting](#interacting)
  * [Advanced](#advanced)
* [Known Issues](#known-issues)

## Installation

1. Clone the repository locally or download and extract the zipped folder.
2. Open config.py
3. Obtain tokens for the Reddit API
    1. Navigate to <https://old.reddit.com/prefs/apps/>
    2. If you have an account, login, if not, create an account
    3. Click on "are you a developer? Create an app..."
    ![image](media/apps.png)
    4. Enter "better-search" for the name of the app
    5. Enter "Searches multiple subreddits and filters results" for the description
    6. Enter "<http://localhost:8080>" for the redirect uri
    ![image](media/newApp.png)
    7. Click on "create app"
    8. In the top left will be a picture of a question mark inside of a diamond
    * To the right of this should be "better-search" and then "personal use script" below that. Below this will be a string of random characters. This is your client id. Navigate to config.py and replace the text that says "your_client_id" with this string.
    * Back on the website, below the client id, should be a section labeled "secret" copy this and replace "your_client_secret" with it.
    * Finally, within the user agent section on config.py, replace your_username with your Reddit username.
        ![image](media/idAndSecret.png)
        ![image](media/config.png)
    * It is now safe to close the browser window.

    * (Optional) the path in "searches_file" can be edited to specify a different file to store saved searches
    * (Optional) the path in "link_output" can be edited to specify a different file to save urls too. See the [Interacting](#interacting) section for more information about this.
    * (Optional) If you prefer to not use fancy characters, or your computer does not support them, change the value of "fancy_characters" to false. This will force the app to use only ASCII characters.

4. Install Python 3 and PIP
    * For ubuntu or Debian based systems:  
        `sudo apt install python3 python3-pip`
5. Install required libraries. They can be found in requirements.txt. Run:  
`pip install -r requirements.txt`
6. For clipboard functionality, either xclip or xsel must be installed. Check if they are installed with `sudo apt show xclip` or `sudo apt show xsel` See the pyperclip documentation (<https://pypi.org/project/pyperclip/>) for more information.

## Usage

Note that the minimum supported terminal size is: **80 columns by 24 rows**

The program can be started by executing the following command, while inside of the project folder:  
    `python3 main.py`

If you receive a message stating that there was a bad HTTP response, you likely have a mistake in your config file. Ensure that the tokens are correct, in quotes, and do not have extra spaces within the quotes.

![image](media/badConfig.png)

The next screen should be a list of names of searches. If the screen states that no searches were found, double check the path to the searches file in config.py.  

![image](media/noSearch.png)

Is that the correct path? If it is, press any key in the terminal to start the process of creating a new search. If it is not, edit the value in config.py, press 'q' in the terminal, and relaunch the program.

### Creating a search  

There are two methods for creating searches: [within the app](#in-app) (easier / recommended) or using [JSON](#json) (advanced / better for power users).  

#### Filters  

There are three different groups of filters and two different filters in each group. The groups are as follows:  

* Title: this is a word or phrase that exists in the title of the post.  
* Flair: this is a word of phrase that exists in the flair of the post. This typically comes after the title on the Reddit site, and is enclosed in some colored oval  
* Post: this is a word or phrase that exists in the main body of the post. It is in the actual contents of the post.

Within each of these groups, there is a blacklist and a whitelist. Blacklisted filters are those that you do not want to see. Whitelisted filters are the ones that will show up as a result of the search. Blacklisted flairs exist to specify certain topics in your results that you do not want to see. Here is an example:  

Lets suppose that you want to perform a search on the Food subreddit, and you are looking for posts that mention pizza, but you absolutely despise onions on pizza. The search for this would look something like this:  

* Pizza -> This is the name of the search (it can be anything)

  * Subreddit: Food -> This is the subreddit that the following rules will apply to

    * Whitelisted Title: pizza -> All posts with the word pizza in the title will be included

    * Blacklisted Title: onion -> All posts with the word onion in the title will be excluded.

Note that posts with a blacklist match will be excluded before posts with a whitelist match will be included. Thus, a post with the title "A delicious onion pizza" will be excluded because the blacklist has higher precedence than the whitelist.

#### In app  

1. On the search creation screen, you will first be prompted to enter the name of the search. This will be the name referenced when you go to perform the search, so choose something relevant and descriptive.
2. Then you will be brought to screen displaying all of the filters associated with that search. At this point, it should show only the name of the seach you just entered.
3. Press 'a' to add a subreddit to the search.
    * You will notice that the subreddits are added to the list, with a number before each one.
4. Press 'e', then enter a number to edit the filters for that subreddit.
5. Press 'e', then enter a number to edit a specific filter.
6. Press 'a' to enter text. This is one of the filters in the category shown at the top.
7. Press 'd', then enter a number to delete the specified filter.
8. Press 'q' to return to the filter category selection screen.
9. Repeat steps 5-8 for each category.
10. Press 'q' to return to the subreddit selection screen.
11. Repeat steps 3-10 for as many subreddits you would like.
12. Press 'q' to exit the search editing screen.
13. You will be prompted asking if you want to save. Enter 'y' to save the search, or 'n' to discard the changes.
    * Note that entering 'n' will not delete the search, it only reverts any changes you just made to it.
14. You will then be brought to a screen that has a list of names of searches. You should see the one you just created at the bottom of this list.

#### JSON  

Search objects are stored using Javascript Object Notation (JSON), and are stored inside a single file. By default, this file is "searches.json", but this can be changed by editing the value of "searches_file" in "config.py". These instructions will only include the necessities for creating a search object, but plenty of information can be found about it online. If you would like a reference file, one can be found at: "<https://github.com/JMGillum/RedditSearch/blob/36b614b9bc63dd9ba60acaf38949963f24e5cef4/searches.json>". To create a search using JSON, open the searches file using a text editor, then:

1. Insert opening and closing curly braces "{}". All of your searches will be housed within these braces.
2. Type `"searches": []` Note that you must include the quotes around searches. The square braces indicate that the value of searches will be a list. Inside of these square braces will be a list of different searches.
3. Each search is its own object. Objects in JSON must be enclosed in curly braces, so include another set of them inside of the square braces.
    * So far your file should look like this:  
    `{"searches":[{}]}`
    * It is typically helpful to seprate items onto newlines. Thus, the following is also valid:

    ```JSON
    {
        "searches": [
            {

            }
        ]
    }
    ```

4. Within these inner braces will be your search object. Start by adding "name": (make sure to include the quotes), then type the name you would like to give the search, also enclosed in quotes, followed by a comma.

5. Next we need to add the time that this search was last performed. This tells the program how far back to search when it performs the search. Add `"lastSearchTime": null`,

6. Next comes the subreddit objects. This is a list of collections of filters applied to a subreddit. If you would like to search multiple subreddits at a time, you need to define the filters for each subreddit individually. Add: "subreddits": [{}]

    ```JSON
    {
        "searches": [
            {
                "name": "food",
                "lastsearchTime": null,
                "subreddits": [
                    {

                    }
                ]
            }
        ]
    }
    ```

7. Next, add the sections for each of the 6 filters. Your file should now look like this:

    ```JSON
        {
            "searches": [
                {
                    "name": "food",
                    "lastsearchTime": null,
                    "subreddits": [
                        {
                        "name": ,
                        "whiteListTitle": [],
                        "blackListTitle": [],
                        "whiteListFlair": [],
                        "blackListFlair": [],
                        "whiteListPost": [],
                        "blackListPost": []
                        }
                    ]
                }
            ]
        }
    ```

    * Notice that there is a comma after each element, except after the last one. This is one of the rules of JSON. It is like describing a list of different items.
8. Add the name of the subreddit that these filters will apply to after "name". Make sure it is enclosed in quotes, and that is is in all lowercase characters.
9. For each filter you would like to use, add different words or phrases, enclosed in quotes, and separated by commas. These should go within their respective square braces. For my example, I will look for hotdogs and hamburgers, and exclude healthy vegetables. My search would look like this:

    ```JSON
        {
            "searches": [
                {
                    "name": "food",
                    "lastsearchTime": null,
                    "subreddits": [
                        {
                            "name": "food",
                            "whiteListTitle": [
                                "hotdog",
                                "hamburger"
                            ],
                            "blackListTitle": [
                                "vegetable",
                                "veggies",
                                "fruit",
                                "healthy"
                            ],
                            "whiteListFlair": [
                                "OC",
                                "Recipe In Comments"
                            ],
                            "blackListFlair": [
                                "Vegetarian",
                            ],
                            "whiteListPost": [
                                "Delicious",
                                "Gourmet",
                                "Amazing"
                            ],
                            "blackListPost": [
                                "Disgusting",
                                "Gross",
                                "Horrible"
                            ]
                        }
                    ]
                }
            ]
        }
    ```

10. If you would like to search another subreddit during this search as well, add a comma after the closing brace of the previous, and repeat the same process.

    ```JSON
        {
            "searches": [
                {
                    "name": "food",
                    "lastsearchTime": null,
                    "subreddits": [
                        {
                            "name": "sub1",
                            ...
                        },
                        {
                            "name": "sub2",
                            ...
                        }
                    ]
                }
            ]
        }
    ```

11. If you wouldl like to define another search, add a comma after the ending curly brace of the previous search, then define another.

    ```JSON
        {
            "searches": [
                {
                    "name": "search1",
                    ...
                },
                {
                    "name": "search2",
                    ...
                }
            ]
        }
    ```

12. Save the file, then execute the program. Do note that changes to this file must be made while the program is **NOT** running.

### Search Selection

On the screen listing searches, you have several options:  

* Press 'a' to allow you to create a new search. Reference the [Creating a search](#creating-a-search) section for help with this.
* Press 'e', 'd', or 'v' to switch to a prompt asking for a number. The number you enter corresponds to the reference numbers of the searches.
  * If 'e' was pressed, this search will then be run. See the Results section for the next steps.
  * If 'd' was pressed, this search will be deleted from the list *Warning! This can not be undone*
  * If 'v' was pressed, this search will then be displayed in a tree form. This is useful for seeing the filters and parameters of the search.
* Press 'q' to close the program.

### Results

* While the search is being performed, you will see a screen that says "Searching..." simply wait and let the search commence.

* After the search is finished, you will see boxes stacked on top of each other vertically. These are the "headers" of your results. Each box corresponds to a single post within your criteria. Each header follows this general form:  

    ```text
    +--------------------------------------------+  
    | Number). Title of post                     |  
    | [Author of post]                           |  
    | ~Flair: flair~                             |  
    | Posted in (subreddit), time minutes ago    |  
    +--------------------------------------------+
    ```

  * The number followed by ')' is the reference number for the post. Viewing a post is discussed in the [Viewing a Post](#viewing-a-post) section.
  * The age is rounded down to the closest significant time period. For example a post that is 80 minutes old will be described as being 1 hour old. A post that is 3 days, 6 hours, and 42 minutes old will be described as being 3 days old.

* The list of boxes can be scrolled through. Pressing the 'w' key or up arrow will scroll everything up a single line. Pressing the 's' or down arrow key will scroll everything down a single line. You can also hold down these keys to scroll faster, and most terminals should allow you to use a mousewheel as well.
* Besides scrolling through the list, you have three other options for input:
  * Pressing 'e' will allow you to enter a number. This number should correspond to a reference number of one of the posts. This will pull up a full screen view of the post, and will contain the actual body text of the post. Reference the Viewing a post section for the next steps.
  * Pressing 'r' will refresh the page. The search will be performed again and any new posts since the last search will be added to the top of the list.
  * Pressing 'q' will quit the program.

### Viewing a post

* Posts viewed in full consist of three sections:
  * Head: This is the first box. Notice that it contains the same contents as the headers found in the navigating results section., except for the reference number. Reference the [Results](#results) section for a description of these.
  * Body: This contains the actual text of the post.
  * Foot: This contains the url of the post. Note that due to limitations of the terminal, this link typically can not be clicked on. You will have to manually copy it over if you want to use it. This link is simply for information. More efficient methods exist for opening the link in a brower, and are described in [Interacting](#interacting)

    ```text
    +--------------------------------------------+  
    | Title of post. This is the head section    |  
    | [Author of post]                           |  
    | ~Flair: flair~                             |  
    | Posted in (subreddit), time minutes ago    |  
    +--------------------------------------------+
    | This is the text of the post, it is the    |  
    | main contents of it. Lorem ipsum dolor sit |
    | amet, consectetur adipiscing elit, sed do  |   
    | eiusmod tempor incididunt ut labore et     | 
    | dolore magna aliqua.                       |    
    +--------------------------------------------+
    | https://www.reddit.com/link_to_the_post    |  
    +--------------------------------------------+
    ```

Press 'h' to bring up a cheatsheet help menu with a description of the available shortcuts. Press any key after this to return to the post.

#### Navigation

* Press or hold 'w' or the up arrow to scroll up
* Press or hold 's' or the down arrow to scroll down
* Press 'a' or the left arrow to shift to the previous post.
* Press 'd' or the right arrow to shift to the next post
* Press 'q' to return to the screen with all of the post headers. Refer to the [Results](#results) section for details on this area

#### Interacting

* Press 'i' to open up the image of the post. This will only do something if it is an image post instead of a text post.
  * A post's type can usually be discerened by the URL at the bottom.
    * A text post will typically start with "www.reddit.com"
    * A repost of an article from outside of reddit will typically have a url that does not have "www.reddit.com" in it.
    * An image post will typically start with "i.redd.it/" and/or it will end with an image's file extension (ex: .jpg, .png)
* Press 'u' to shift to another screen that displays a file name. All of the links in the post have been written to that file. Links are written in the order they are added. So the newest links will be at the bottom of the file. After you have viewed the links, it is safe to delete them from the file.  

The following shortcuts will open a page on the official Reddit website, in your default web browser:

* press 'o' to open the post
* Press 'm' to open the post author's page

### Advanced

* If you know which search you want to perform ahead of time, you can save time by specifying it in the command line. To do this, run:  

```python
    python3 main.py -n <search_name>
```  

* Do note that search names are case sensitive, such that "mysearch" is not the same as "MYSEARCH". If you specify a search that does not exist, the program will list out all available searches that are present in the specified search file.  
* Add a '-d' flag to prevent the lastSearchTime variable from being modified. This is useful if you want to run the search multiple times over the same timeframe.
* Add a '-y' flag to automatically agree to prompts asking if you want to run a search that hasn't be run in a while (typically over a week)

## Known Issues

* Currently none :)
