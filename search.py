from tree import Tree

class Filter:
    def __init__(self,name=None,content=None):
        # name is str, content is list of strings
        self.name = ""
        self.content = ""
        self.update(name,content)


    def update(self,name=None,content=None):
        if name is not None and isinstance(name,str):
            self.name = name
        if content is not None and isinstance(content,list):
            self.content = content
    
    
    def add(self,content=None):
        if content is not None:
            if not isinstance(content, list):
                content = [content]
            if self.content is not None:
                self.content += content
            else:
                self.content = content
    


class SubredditSearch:
    def __init__(
        self,
        sub=None,
        titleWL=None,
        titleBL=None,
        flairWL=None,
        flairBL=None,
        postWL=None,
        postBL=None,
    ):
        self.name = sub
        self.titleWL = Filter(name="Title White List")
        self.titleBL = Filter(name="Title Black List")
        self.flairWL = Filter(name="Flair White List")
        self.flairBL = Filter(name="Flair Black List")
        self.postWL = Filter(name="Post White List")
        self.postBL = Filter(name="Post Black List")

    def update(
        self,
        sub=None,
        titleWL=None,
        titleBL=None,
        flairWL=None,
        flairBL=None,
        postWL=None,
        postBL=None,
    ):
        # Updates values if they are presented
        if sub is not None:
            self.name = sub
        self.titleWL.update(titleWL)
        self.titleBL.update(titleBL)
        self.flairWL.update(flairWL)
        self.flairBL.update(flairBL)
        self.postWL.update(postWL)
        self.postBL.update(postBL)
        
    def add(
        self,
        titleWL=None,
        titleBL=None,
        flairWL=None,
        flairBL=None,
        postWL=None,
        postBL=None,
    ):
       
       self.titleWL.add(titleWL)
       self.titleBL.add(titleBL) 
       self.flairWL.add(flairWL)
       self.flairBL.add(flairBL)
       self.postWL.add(postWL)
       self.postBL.add(postBL)


class Search:
    def __init__(self, name=None, lastSearchTime=None, subreddits=None):
        self.name = name
        self.lastSearchTime = lastSearchTime
        self.subreddits = subreddits

    def addSub(self, subSearch):
        if isinstance(subSearch, SubredditSearch):
            if self.subreddits is not None:
                self.subreddits.append(subSearch)
            else:
                if not isinstance(subSearch, list):
                    self.subreddits = [subSearch]
                else:
                    self.subreddits = subSearch

    def update(self, name=None, lastSearchTime=None, subreddits=None):
        # Updates values if they are presented
        if name is not None:
            self.name = name
        if lastSearchTime is not None:
            self.lastSearchTime = lastSearchTime
        if subreddits is not None:
            self.subreddits = subreddits
