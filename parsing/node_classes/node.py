from parsing.utils.node_tree_str import NodeTreeStr

class Node(object):

    def __init__(self, node):
        self.node = node

    def __str__(self):
        return str(NodeTreeStr(self.node))