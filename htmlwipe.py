# -*- coding: utf-8 -*-

from __future__ import division

import sys
from pprint import pprint
from json import dumps
from StringIO import StringIO

import lxml.html
from lxml import etree

from einfo import EInfo
from list_utils import distance_between_sorted_arrays
from tree_utils import traverse_wide, print_tree
from xpath_utils import xpath_for_es



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


def collect_info_by_es(es):
    return map(lambda x: EInfo(x).info(), es)


def print_ess(ess, root=None):
    print "Traverse: detected %s structures:\n" % len(ess)
    if not ess: return
    pprint(ess)
    print "\nDetailed:"
    for es in ess:
        print "=" * 20
        if root:
            xpath, errstring = xpath_for_es(es, root)
            print "%s items." % len(es), "NOT Suggested: %s." % errstring if errstring else "", "calculated XPATH: ", xpath
        print_es(es)
            #print construct_parentpath_for_tree(e)
        print


def print_es(es):
    for e in es:
        print "-" * 10, e
        print etree.tounicode(e, method="html", pretty_print=True)
        #print_tree(e)


def item_info_from_es(es):
    if not es:
        return
    
    e = es[0]
    i = EInfo(e)
    i.info()
    if i.urls and False:
        c = EInfo(i.urls[0][0])
        #print i.childpath(i.urls[0][0])
        print c.search_for_xpath(e, 1, relroot=e)

    #pprint(i.e.findall(".//*"))
    _es =  i.e.xpath(u".//*[contains(text(), '$')] | .//*[contains(text(), '€')] | .//*[contains(text(), 'EUR')] | .//*[contains(text(), 'USD')] | .//*[contains(text(), 'GBP')]")
    #print i.e.xpath(".//*[contains(text(), 'Filet')]")
    print_es(_es)


def main_html(text):
    html = lxml.html.parse(StringIO(text))
    root = html.getroot()
    #root = lxml.html.document_fromstring(text)

    ess = traversal(root, 1, min_elements=4,
              mintreeheight=3, maxtreeheight=4, maxmismatch=0.28)
    print_ess(ess, root=root)

    print "ITEM INFO"
    for es in ess:
        item_info_from_es(es)


def main_filename(filename):
    text = open(filename).read()
    return main(text)


def main():
    #FILE = "htmls/frankonia.fr.html"
    FILE = "examples/naturabuy.fr.html"
    #FILE = "htmls/cariboom.com.html"
    #FILE = "htmls/Veniard Esmond Dury Trebles Nickel Plated   Ted Carter Fishing Tackle.html"
    text = open(FILE).read()
    main_html(text)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '-':
            text = sys.stdin.read()
            main_html(text)
        else:
            main_filename(sys.argv[1])
    else:
        main()
