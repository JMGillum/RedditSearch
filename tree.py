class Tree:
    fancy = False
    pipe = "|"
    branch = "|->"
    end = "|->"
    space = "  "
    spaceStart = ""
    string = ""
    def __init__(self,name : str, nodes : list | None):
        self.set_name(name)
        self.set_nodes(nodes)
        self.dirty = True
        
    
    def set_name(self,name:str):
        self.name = name
        self.dirty = True
    

    def set_nodes(self,nodes: list | None):
        self.nodes = nodes
        self.dirty = True
        
        
    def set_fancy(set_fancy: bool):
        Tree.fancy = set_fancy
        Tree.set_characters()
        
        
    def set_characters():
        if Tree.fancy:
            Tree.pipe = "│"
            Tree.branch = "├─"
            Tree.end = "└─"
            Tree.space = " "
        else:
            Tree.pipe = "|"
            Tree.branch = "|->"
            Tree.end = "|->"
            Tree.space = "  "
            Tree.spaceStart = ""


    def to_string(self):
        if self.dirty: # Doesn't regenerate tree if no changes have been made.
            # Sets entire tree as the single child node of tree. Necessary for proper spacing
            # Saves values so they can be restored after building tree
            name = self.name
            nodes = self.nodes
            child = Tree(name,nodes)
            self.name = None
            self.nodes = [child]
            # Gets the tree, as a list of lines
            string = self.print(True)
            # Converts the list to a single string
            self.string = ""
            for line in string:
                self.string += line
            # Restores the original values of the name and nodes.
            self.name = name
            self.nodes = nodes
            self.dirty = False
        return self.string


    def print(self,last=False):
        """Generates a tree, recursively

        Args:
            last (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        string = []
        if self.name:
            if last:
                string.append(f"{self.end}{self.name}\n")
            else:
                string.append(f"{self.branch}{self.name}\n")
        for i in range(len(self.nodes)):
            item = self.nodes[i]
            if isinstance(item,str):
                if(i == len(self.nodes)-1):
                    string.append(Tree.end)
                else:
                    string.append(Tree.branch)
                string[-1] += f"{item}\n"
            elif isinstance(item,Tree):
                child_last = (i == len(self.nodes)-1)
                child = item.print(child_last)
                for j in range(1,len(child)):
                    line = child[j]
                    if(i != len(self.nodes) - 1):
                        child[j] = Tree.pipe
                    else:
                        child[j] = Tree.space
                    child[j] += f"{Tree.space}{line}" 
                string += child
        return string
    


def placeItem(name, showBeginning, showMiddle, last, width=80, fancy=False):
    """
    Used by search tree for the third tier items
    """
    pipe = "|"
    branch = "|->"
    end = "|->"
    space = "  "
    spaceStart = ""
    if fancy:
        pipe = "│"
        branch = "├─"
        end = "└─"
        space = " "

    if showBeginning:
        string = f"{spaceStart}{pipe}"
    else:
        string = f"{spaceStart} "

    if showMiddle:
        string = f"{string}{space}{pipe}"
    else:
        string = f"{string}{space} "
    if last:
        string = f"{string}{space}{end}"
    else:
        string = f"{string}{space}{branch}"

    lenTest = f"{spaceStart}{pipe}{space}{pipe}{space}{branch}"
    if len(name) > ((width - 1) - len(lenTest)):
        name = f"{name[:(width-4)-(len(lenTest))]}..."

    return f"{string}{name}"


def placeTitle(name, showBeginning, last, fancy=False):
    """
    Used by search tree for the second tier items
    """

    pipe = "|"
    branch = "|->"
    end = "|->"
    space = "  "
    spaceStart = ""
    if fancy:
        pipe = "│"
        branch = "├─"
        end = "└─"
        space = " "

    if showBeginning:
        string = f"{spaceStart}{pipe}"
    else:
        string = f"{spaceStart} "
    if last:
        string = f"{string}{space}{end}"
    else:
        string = f"{string}{space}{branch}"

    return f"{string}{name}"


def filterTree(
    name, filterName, filterContents, width=80, fancy=False, enumerate=False
):
    stringList = []
    stringList.append(name)
    stringList.append(placeTitle(filterName, False, True, fancy))
    if filterContents is not None and len(filterContents) > 0:
        numItems = 0
        ticker = 0
        for item in filterContents:
            numItems = numItems + 1
            last = numItems == len(filterContents)
            ticker = ticker + 1
            if enumerate:
                stringList.append(
                    placeItem(f"{ticker}. {item}", False, False, last, width, fancy)
                )
            else:
                stringList.append(placeItem(item, False, False, last, width, fancy))
    return stringList


def subTree(sub, width=80, fancy=False):
    stringList = []
    if sub is not None:
        finalSub = False

        stringList.append(sub.name)
        stringList.append(placeTitle("1. Title whitelist", finalSub, False, fancy))
        if sub.titleWL is not None and len(sub.titleWL) > 0:
            numItems = 0
            for item in sub.titleWL:
                numItems = numItems + 1
                last = numItems == len(sub.titleWL)
                stringList.append(placeItem(item, finalSub, True, last, width, fancy))

        stringList.append(placeTitle("2. Title blacklist", finalSub, False, fancy))
        if sub.titleBL is not None and len(sub.titleBL) > 0:
            numItems = 0
            for item in sub.titleBL:
                numItems = numItems + 1
                last = numItems == len(sub.titleBL)
                stringList.append(placeItem(item, finalSub, True, last, width, fancy))

        stringList.append(placeTitle("3. Flair whitelist", finalSub, False, fancy))
        if sub.flairWL is not None and len(sub.flairWL) > 0:
            numItems = 0
            for item in sub.flairWL:
                numItems = numItems + 1
                last = numItems == len(sub.flairWL)
                stringList.append(placeItem(item, finalSub, True, last, width, fancy))

        stringList.append(placeTitle("4. Flair blacklist", finalSub, False, fancy))
        if sub.flairBL is not None and len(sub.flairBL) > 0:
            numItems = 0
            for item in sub.flairBL:
                numItems = numItems + 1
                last = numItems == len(sub.flairBL)
                stringList.append(placeItem(item, finalSub, True, last, width, fancy))

        stringList.append(placeTitle("5. Post whitelist", finalSub, False, fancy))
        if sub.postWL is not None and len(sub.postWL) > 0:
            numItems = 0
            for item in sub.postWL:
                numItems = numItems + 1
                last = numItems == len(sub.postWL)
                stringList.append(placeItem(item, finalSub, True, last, width, fancy))

        stringList.append(placeTitle("6. Post blacklist", finalSub, True, fancy))
        if sub.postBL is not None and len(sub.postBL) > 0:
            numItems = 0
            for item in sub.postBL:
                numItems = numItems + 1
                last = numItems == len(sub.postBL)
                stringList.append(placeItem(item, finalSub, False, last, width, fancy))
    return stringList


def searchTree(search, width=80, fancy=False, enumerate=False):
    """
    Returns a list of strings representing a tree-style view of a search
    """
    if search is not None:
        stringList = []
        if search.name is not None:
            stringList.append(search.name)
            if search.subreddits is not None:
                if fancy:
                    tierOne = "├─"
                    tierOneLast = "└─"
                else:
                    tierOne = "|->"
                    tierOneLast = tierOne

                subNum = 0
                lastSub = len(search.subreddits)
                finalSub = True
                for sub in search.subreddits:
                    subNum = subNum + 1
                    if subNum >= lastSub:
                        finalSub = False
                    if sub.titleWL is not None and len(sub.titleWL) > 0:
                        subLast = 0
                    if sub.titleBL is not None and len(sub.titleBL) > 0:
                        subLast = 1
                    if sub.flairWL is not None and len(sub.flairWL) > 0:
                        subLast = 2
                    if sub.flairBL is not None and len(sub.flairBL) > 0:
                        subLast = 3
                    if sub.postWL is not None and len(sub.postWL) > 0:
                        subLast = 4
                    if sub.postBL is not None and len(sub.postBL) > 0:
                        subLast = 5

                    if finalSub is False:
                        if enumerate:
                            stringList.append(f"{tierOneLast}{subNum}.{sub.name}")
                        else:
                            stringList.append(f"{tierOneLast}{sub.name}")
                    else:
                        if enumerate:
                            stringList.append(f"{tierOne}{subNum}.{sub.name}")
                        else:
                            stringList.append(f"{tierOne}{sub.name}")
                    if sub.titleWL is not None and len(sub.titleWL) > 0:
                        stringList.append(
                            placeTitle("Title whitelist", finalSub, subLast == 0, fancy)
                        )
                        numItems = 0
                        for item in sub.titleWL:
                            numItems = numItems + 1
                            last = numItems == len(sub.titleWL)
                            if subLast == 0:
                                stringList.append(
                                    placeItem(item, finalSub, False, last, width, fancy)
                                )
                            else:
                                stringList.append(
                                    placeItem(item, finalSub, True, last, width, fancy)
                                )

                    if sub.titleBL is not None and len(sub.titleBL) > 0:
                        stringList.append(
                            placeTitle("Title blacklist", finalSub, subLast == 1, fancy)
                        )
                        numItems = 0
                        for item in sub.titleBL:
                            numItems = numItems + 1
                            last = numItems == len(sub.titleBL)
                            if subLast == 1:
                                stringList.append(
                                    placeItem(item, finalSub, False, last, width, fancy)
                                )
                            else:
                                stringList.append(
                                    placeItem(item, finalSub, True, last, width, fancy)
                                )

                    if sub.flairWL is not None and len(sub.flairWL) > 0:
                        numItems = 0
                        stringList.append(
                            placeTitle("Flair whitelist", finalSub, subLast == 2, fancy)
                        )
                        for item in sub.flairWL:
                            numItems = numItems + 1
                            last = numItems == len(sub.flairWL)
                            if subLast == 2:
                                stringList.append(
                                    placeItem(item, finalSub, False, last, width, fancy)
                                )
                            else:
                                stringList.append(
                                    placeItem(item, finalSub, True, last, width, fancy)
                                )

                    if sub.flairBL is not None and len(sub.flairBL) > 0:
                        numItems = 0
                        stringList.append(
                            placeTitle("Flair blacklist", finalSub, subLast == 3, fancy)
                        )
                        for item in sub.flairBL:
                            numItems = numItems + 1
                            last = numItems == len(sub.flairBL)
                            if subLast == 3:
                                stringList.append(
                                    placeItem(item, finalSub, False, last, width, fancy)
                                )
                            else:
                                stringList.append(
                                    placeItem(item, finalSub, True, last, width, fancy)
                                )

                    if sub.postWL is not None and len(sub.postWL) > 0:
                        numItems = 0
                        stringList.append(
                            placeTitle("Post whitelist", finalSub, subLast == 4, fancy)
                        )
                        for item in sub.postWL:
                            numItems = numItems + 1
                            last = numItems == len(sub.postWL)
                            if subLast == 4:
                                stringList.append(
                                    placeItem(item, finalSub, False, last, width, fancy)
                                )
                            else:
                                stringList.append(
                                    placeItem(item, finalSub, True, last, width, fancy)
                                )

                    if sub.postBL is not None and len(sub.postBL) > 0:
                        numItems = 0
                        stringList.append(
                            placeTitle("Post blacklist", finalSub, subLast == 5, fancy)
                        )
                        for item in sub.postBL:
                            numItems = numItems + 1
                            last = numItems == len(sub.postBL)
                            if subLast == 5:
                                stringList.append(
                                    placeItem(item, finalSub, False, last, width, fancy)
                                )
                            else:
                                stringList.append(
                                    placeItem(item, finalSub, True, last, width, fancy)
                                )
        return stringList
    else:
        return None
