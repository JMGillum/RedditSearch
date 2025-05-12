from tree import Tree

class Filter:
    def __init__(self,name=None,content=None):
        # name is str, content is list of strings
        self.name = ""
        self.content = ""
        self.tree = Tree()
        self.update(name,content)


    def update(self,name=None,content=None):
        if name is not None and isinstance(name,str):
            self.name = name
            self.tree.set_name(name)
        if content is not None and isinstance(content,list):
            self.content = content
            self.tree.set_nodes(content)    

    
    def add(self,content=None):
        if content is not None:
            if not isinstance(content, list):
                content = [content]
            if self.content is not None:
                self.content += content
            else:
                self.content = content
            self.tree.set_nodes(self.content)
    


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
        self.titleWL = Filter(name="Title White List",content=titleWL)
        self.titleBL = Filter(name="Title Black List",content=titleBL)
        self.flairWL = Filter(name="Flair White List",content=flairWL)
        self.flairBL = Filter(name="Flair Black List",content=flairBL)
        self.postWL = Filter(name="Post White List",content=postWL)
        self.postBL = Filter(name="Post Black List",content=postBL)
        self.tree = Tree(name=self.name, nodes=[self.titleWL.tree,self.titleBL.tree,self.flairWL.tree,self.flairBL.tree,self.postWL.tree,self.postBL.tree])

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
        self.name = ""
        self.lastSearchTime = 0
        self.subreddits = None
        self.tree = Tree()
        self.update(name,lastSearchTime,subreddits)

    def addSub(self, subSearch):
        if isinstance(subSearch, SubredditSearch):
            if self.subreddits is not None:
                self.subreddits.append(subSearch)
            else:
                if not isinstance(subSearch, list):
                    self.subreddits = [subSearch]
                else:
                    self.subreddits = subSearch
            nodes = []
            for sub in self.subreddits:
                nodes.append(sub.tree)
            self.tree.set_nodes(nodes)

    def update(self, name=None, lastSearchTime=None, subreddits=None):
        # Updates values if they are presented
        if name is not None:
            self.name = name
            self.tree.set_name(self.name)
        if lastSearchTime is not None:
            self.lastSearchTime = lastSearchTime
        if subreddits is not None:
            self.subreddits = subreddits
            nodes = []
            for sub in self.subreddits:
                nodes.append(sub.tree)
            self.tree.set_nodes(nodes)
