client_id="your_client_id" # your client id
client_secret="your_client_secret" # your client secret
user_agent="Python:better-search:v1.0.0 (by u/your_username)" # your user agent

searches_file="searches.json" # Default is searches.json. Change this value to use a different file
link_output="links.txt" # This is where urls are saved when you request to save them

fancy_characters=True # Default is True. Change to False if there are issues with rendering the following: '┌ ┐ └ ┘ ├ ┤ │ ─'
praw_check=True # Checking that praw is functioning. Should always be True. Change to False only for debugging
term_size_check=True # Checks if the terminal size is large enough. Should always be True