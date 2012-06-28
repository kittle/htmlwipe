# -*- coding: utf-8 -*-

from __future__ import division

import sys
from pprint import pprint
from json import dumps
from StringIO import StringIO

import lxml.html

from array_utils import distance_between_sorted_arrays
from tree_utils import traverse_wide, traverse_deep

from xpath_utils import xpath_by, verify_xpath


def str_element(e):
    attrib = " ".join(['%s="%s"' % (k,v) for k,v in e.attrib.items()])
    return "<%s%s>%s%s" % (e.tag, " " + attrib if attrib else "",
                             " " + e.label.strip() if e.label and e.label.strip() else "",
                             " " + e.text.strip() if e.text and e.text .strip() else "" )


def tree_hash(t, minlevel=0, maxlevel=None):
    """
    Array "hash" here is a list of elements(html) tags from tree which are traversed wide up to maxlevel.
    Return None if tree has less than minlevel .
    """
    hash = traverse_wide(t, todo=lambda x: x.tag, minlevel=minlevel, maxlevel=maxlevel)
    return hash


def compare_trees(t1, t2, maxmismatch=0.2, minlevel=3, maxlevel=4):
    """
    Compare two trees by some artificial metric. 
    """
    hash1 = tree_hash(t1, minlevel=minlevel, maxlevel=maxlevel)
    hash2 = tree_hash(t2, minlevel=minlevel, maxlevel=maxlevel)

    if hash1 is None or hash2 is None:
        return False

    min_len = max(min(len(hash1), len(hash2)), 1)
    distance = distance_between_sorted_arrays(sorted(hash1),
                                   sorted(hash2))
    level = distance / min_len
    if  level <= maxmismatch:
        return True
    return False


def traversal(root, level, min_elements=4,
              mintreeheight=3, maxtreeheight=4, maxmismatch=0.2, debug=False):
    """
    Detect a sequences of similar structures in html. Ex: products, forms, polls on a webpage.
    Each sequence has:
    1. not less than min_elements
    2. not less than mintreeheight
    3. everything started from maxtreeheight is unimportant
    4. similarity should be less than maxmismatch
    """
    
    ret = []
    
    first = None
    prev = None
    n = 0
    #print "level: ", level
    subret = []
    childrens = root.getchildren()
    for ch in childrens:
        if prev is not None:
            if compare_trees(ch, prev,
                    minlevel=mintreeheight, maxlevel=maxtreeheight, maxmismatch=maxmismatch):
                if first is None:
                    first = prev
                    n += 1
                n += 1
                subret.append(ch)
            else:
                if n >= min_elements:
                    if debug:
                        print "FINISH: %s %s %s %s" % (level, n, ch.tag, first)
                    subret.insert(0, first)
                    ret.append(subret)
                # reseting
                n = 0
                first = None
                subret = []

        prev = ch
        ret.extend(
                   traversal(ch, level+1, min_elements=min_elements,
              mintreeheight=mintreeheight, maxtreeheight=maxtreeheight, maxmismatch=maxmismatch))
    else: # end of child list
        if n >= min_elements:
            if debug:
                print "FINISH: %s %s %s %s" % (level, n, ch.tag, first)
            subret.insert(0, first)
            ret.append(subret)
    return ret


def print_special(spec):
    for level, e in spec:
        print "  "*(level-1), e


def print_tree(root):
    print_special(traverse_deep(root, todo=str_element))


def construct_parentpath_for_tree(e, separator=" -> "):
    ei = EInfo(e)
    return ei.parentpath_tuples()


class EInfo():
    
    def __init__(self, e):
        assert not isinstance(e, list)
        self.e = e
    
    def __repr__(self):
        return repr(self.e)
    
    def info(self):
        self.urls = map(lambda x: (x, x.get("href")), self.e.findall(".//a"))
        self.imgs = map(lambda x: (x, x.get("src")), self.e.findall(".//img"))
        self.text = filter(lambda x: x[1], map(lambda x: (x, x.text_content()), self.e.findall(".//*")))

    def find(self, s):
        "very simple"
        ret = []
        for e in self.e.iterdescendants():
            for v in e.values():
                if s in v:
                    ret.append(e)
        return ret

    def parentpath(self, root=None):
        e = self.e
        do = True
        ret = []
        while do:
            ret.insert(0, e)
            e = e.getparent()
            if not e or e == root:
                do = False
        return ret

    def parentpath_str(self, root=None, separator=" -> "):
        ret = self.parentpath(root=root)
        return separator.join(
                map(lambda x: "%s(%s)" % (x.tag, x.attrib), ret))

    def parentpath_tuples(self, root=None):
        ret = self.parentpath(root=root)
        return map(lambda x: (x.tag, x.items()), ret)


    def create_xpath(self, root=None):
        path = self.parentpath(root=root)

        ret = []
        for e in path:
            if e.keys():
                k,v = e.items()[0]
                ret.append("{}[@{}='{}']".format(e.tag, k, v))
            else:
                ret.append(e.tag)
    
        return ("./" if root else "/") + "/".join(ret)


def collect_info_by_es(es):
    info = map(EInfo, es)
    map(lambda x: x.info(), info)
    return info


def xpath_for_es(es, text):
    #pprint(es)
    paths = map(lambda x: construct_parentpath_for_tree(x), es)
    #pprint(paths)
    xpath = xpath_by(paths)
    errstring = verify_xpath(xpath, text, paths)
    return xpath, errstring


def print_ess(ess, text=None):
    print "Traverse: detected %s structures:\n" % len(ess)
    if not ess: return
    pprint(ess)
    print "\nDetailed:"
    for es in ess:
        print "=" * 20
        if text:
            xpath, errstring = xpath_for_es(es, text)
            print "NOT Suggested: %s." % errstring if errstring else "", "calculated XPATH: ", xpath
        for e in es:
            print "-" * 10, e
            print_special(traverse_deep(e, todo=str_element))
            #print construct_parentpath_for_tree(e)
        print


def main(text):
    html = lxml.html.parse(StringIO(text))
    root = html.getroot()

    ess = traversal(root, 1, min_elements=4,
              mintreeheight=3, maxtreeheight=4, maxmismatch=0.28)

    print_ess(ess, text=text)


def main_filename(filename):
    text = open(filename).read()
    return main(text)


def test():
    """
    es = root.xpath("//div[@class='products']/ul/li")
    for e in es:
        print compare_trees(es[0], e)
    return
    """
    """
    es = root.xpath("//div[@class='products']/ul/li")
    e1 = tree_hash(es[0])
    e2 = tree_hash(es[1])
    e1 = sorted(e1)
    e2 = sorted(e2)
    print e1
    print e2
    print distance_between_sorted_arrays(e1, e2)
    return
    for e in es:
        pprint(traverse_wide(e, maxlevel=3, todo=lambda x: x.tag))
        #pprint(traverse_wide(e, maxlevel=3, todo=print_tree))
    return

    print compare_trees(p[0], p[1])
    print compare_trees(p[2], p[3])
    return
    
    p = root.xpath("//div[@class='products']")
    es = traversal(p[0], 1)
    print_tree(p[0])
    return
    """
    for es in ess:
        info = collect_info_by_es(es)
        #pprint(info)
        
        r = map(lambda x: x.find("html"), info)
        #print EInfo(r[0][0]).parentpath_str(root=ess[0][0])
        print EInfo(r[0][0]).create_xpath(root=ess[0][0])
        #pprint()
        return

    return

    print dumps(map(
               lambda es: map(lambda x: construct_parentpath_for_tree(x), es),
               ess))


if __name__ == "__main__":
    #FILE = "htmls/frankonia.fr.html"
    FILE = "htmls/naturabuy.fr.html"
    #FILE = "htmls/cariboom.com.html"
    #FILE = "htmls/Veniard Esmond Dury Trebles Nickel Plated   Ted Carter Fishing Tackle.html"

    main_filename(sys.argv[1])
