import xml.etree.ElementTree as ET
import re


class object_dict(dict):
    """object view of dict, you can
    >>> a = object_dict()
    >>> a.fish = 'fish'
    >>> a['fish']
    'fish'
    >>> a['water'] = 'water'
    >>> a.water
    'water'
    >>> a.test = {'value': 1}
    >>> a.test2 = object_dict({'name': 'test2', 'value': 2})
    >>> a.test, a.test2.name, a.test2.value
    (1, 'test2', 2)
    """
    def __init__(self, initd=None):
        if initd is None:
            initd = {}
        dict.__init__(self, initd)

    def __getattr__(self, item):

        try:
            d = self.__getitem__(item)
        except KeyError:
            return None # Crazy hack to make Django template work better...

        if isinstance(d, dict) and 'value' in d and len(d) == 1:
            return d['value']
        else:
            return d

        # if value is the only key in object, you can omit it

    def __setattr__(self, item, value):
        self.__setitem__(item, value)

    def getvalue(self, item, value=None):
        return self.get(item, {}).get('value', value)


def _parse_node(node):
    node_tree = object_dict()
    # Save attrs and text, hope there will not be a child with same name
    if node.text:
        # If this is a leaf node with no attributes, then flaten the
        # value attribute
        if node.getchildren() == [] and node.attrib == {}:
            return node.text
        else:
            if node.text.strip() != '':
                node_tree.value = node.text
    for (k, v) in node.attrib.items():
        k, v = _namespace_split(k, object_dict({'value':v}))
        node_tree[k] = v
    #Save childrens
    for child in node.getchildren():
        tag, tree = _namespace_split(child.tag,
                                     _parse_node(child))
        if tag not in node_tree:  # the first time, so store it in dict
            node_tree[tag] = tree
            continue
        old = node_tree[tag]
        if not isinstance(old, list):
            node_tree.pop(tag)
            node_tree[tag] = [old]  # multi times, so change old dict to a list
        node_tree[tag].append(tree)  # add the new one

    return node_tree


def _namespace_split(tag, value):
    """
    Split the tag '{http://cs.sfsu.edu/csc867/myscheduler}patients'
    ns = http://cs.sfsu.edu/csc867/myscheduler
    name = patients
    """
    result = re.compile("\{(.*)\}(.*)").search(tag)
    if result:
        namespace, tag = result.groups()

    return (tag, value)


def parse(file):
    """parse a xml file to a dict"""
    f = open(file, 'r')
    return fromstring(f.read())


def fromstring(s, encoding='utf-8'):
    """parse a string"""
    try:
        if s isinstance(unicode):
            s = s.encode(encoding)
        t = ET.fromstring(s)
    except ET.ParseError:
        return s
    
    root_tag, root_tree = _namespace_split(t.tag, _parse_node(t))
    return object_dict({root_tag: root_tree})
