import asciitree

class NodeTreeStr(object):

    def __init__(self, node, file=''):
        self.node = node
        self.file = file

    def __str__(self):
        return self._node_tree_str()

    ##### Private methods #####

    def _node_children(self, node):
        list_ret = []
        for c in node.get_children():
            if self.file:
                if self.file == c.location.file.name:
                    list_ret.append(c)
            else:
                list_ret.append(c)
        return list_ret

    def _node_str(self, node):
        text = node.spelling or node.displayname
        try:
            kind = str(node.kind)[str(node.kind).index('.')+1:]
        except Exception as e:
            kind = "UNKNOWN KIND"
        return '{} {}'.format(kind, text)

    def _node_tree_str(self):
        return asciitree.draw_tree(self.node, self._node_children, self._node_str)