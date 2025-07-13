import json

def serializeFilter(filter):
    if filter is not None:
        if filter.content is not None and len(filter.content) > 0:
            string = "["
            for item in filter.content:
                string += f"'{item}',"
            string = string[:-1]
            string += "]"
            string = string.replace("'",'"')
            string = string.replace("None","null")
            return string
    return "null"
            

def serializeSub(sub):
    """
    Serializes a SubredditSearch object into a string format
    * sub is the SubredditSearch object to be serialized
    """
    if sub is not None:
        string = f'"name":"{sub.name}", "whiteListTitle":{serializeFilter(sub.titleWL)}, "blackListTitle":{serializeFilter(sub.titleBL)}, "whiteListFlair":{serializeFilter(sub.flairWL)}, "blackListFlair":{serializeFilter(sub.flairBL)}, "whiteListPost":{serializeFilter(sub.postWL)}, "blackListPost":{serializeFilter(sub.postBL)}'
        string = "{" + string + "}"
        string = string.replace("'", '"')
        string = string.replace("None", "null")
        return string
    return ""


def serializeSearch(search):
    """
    Serializes a single Search object into a string format
    """
    if search is not None:
        string = f'"name":"{search.name}", "lastSearchTime":{search.lastSearchTime}, "subreddits":['
        for item in search.subreddits:
            string = string + serializeSub(item) + ","

        string = string.rstrip(",")
        string = string + "]"
        string = "{" + string + "}"
        string = string.replace("'", '"')
        string = string.replace("None", "null")
        return string
    return ""


def serializeSearches(searches):
    """
    Serializes a list of Search objects into a string format
    """
    if searches is not None:
        if not isinstance(searches, list):
            searches = [searches]
        string = '"searches":['
        for item in searches:
            string = string + serializeSearch(item) + ","

        string = string.rstrip(",")
        string = string + "]"
        string = "{" + string + "}"
        string = string.replace("'", '"')
        string = string.replace("None", "null")

        return string
    return ""


def saveSearches(searches, filepath="searches.json"):
    """
    Writes a list of searches to file.
    """
    dumpStr = serializeSearches(searches)
    parsed = json.loads(dumpStr)
    with open(filepath, "w") as write:
        json.dump(parsed, write, indent=2)
