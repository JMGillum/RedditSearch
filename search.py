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
        self.titleWL = titleWL
        self.titleBL = titleBL
        self.flairWL = flairWL
        self.flairBL = flairBL
        self.postWL = postWL
        self.postBL = postBL

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
        if titleWL is not None:
            self.titleWL = titleWL
        if titleBL is not None:
            self.titleBL = titleBL
        if flairWL is not None:
            self.flairWL = flairWL
        if flairBL is not None:
            self.flairBL = flairBL
        if postWL is not None:
            self.postWL = postWL
        if postBL is not None:
            self.postBL = postBL

    def add(
        self,
        titleWL=None,
        titleBL=None,
        flairWL=None,
        flairBL=None,
        postWL=None,
        postBL=None,
    ):
        if titleWL is not None:
            if not isinstance(titleWL, list):
                titleWL = [titleWL]
            if self.titleWL is not None:
                self.titleWL += titleWL
            else:
                self.titleWL = titleWL

        if titleBL is not None:
            if not isinstance(titleBL, list):
                titleBL = [titleBL]
            if self.titleBL is not None:
                self.titleBL += titleBL
            else:
                self.titleBL = titleBL

        if flairWL is not None:
            if not isinstance(flairWL, list):
                flairWL = [flairWL]
            if self.flairWL is not None:
                self.flairWL += flairWL
            else:
                self.flairWL = flairWL

        if flairBL is not None:
            if not isinstance(flairBL, list):
                flairBL = [flairBL]
            if self.flairBL is not None:
                self.flairBL += flairBL
            else:
                self.flairBL = flairBL

        if postWL is not None:
            if not isinstance(postWL, list):
                postWL = [postWL]
            if self.postWL is not None:
                self.postWL += postWL
            else:
                self.postWL = postWL

        if postBL is not None:
            if not isinstance(postBL, list):
                postBL = [postBL]
            if self.postBL is not None:
                self.postBL += postBL
            else:
                self.postBL = postBL


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
