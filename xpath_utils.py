
from json import loads
from pprint import pprint

import lxml.html
#from scrapy.selector import XPathSelector, XmlXPathSelector, HtmlXPathSelector

from einfo import EInfo


def create_xpath(path, root=None):
    def toxp(path):
        ret = []
        for tag, atrs in path:
            #print atrs
            if atrs:
                k,v = atrs[0]
                #ret.append(tag)
                ret.append("{}[@{}='{}']".format(tag, k, v))
            else:
                ret.append(tag)
        return ret
    
    p = ("/" if root is None else "./")  + "/".join(toxp(path))
    return p



def calculate_common_path(paths):
    
    def is_paths_has_same_tag(tag, i, paths):
        for path in paths:
            if path[i][0] != tag:
                return False
        return True
    
    assert len(paths)
    ret = []
    first = paths[0]
    #pprint(first)
    for i, s in enumerate(first):
        ftag, fitems = s
        #print ftag  
        for path in paths[1:]:
            tag, items = path[i]
            #print ftag, tag
            if ftag != tag:
                return ret
            if sorted(fitems) != sorted(items):
                #special case
                if is_paths_has_same_tag(ftag, i, paths):
                    ret.append([ftag, []])
                return ret
        ret.append(s)
    return ret


def xpath_by(paths):
    common_path = calculate_common_path(paths)
    xpath = create_xpath(common_path)
    return xpath
    #return verify_xpath(xpath, html, paths), xpath


def verify_xpath(xpath, root, paths):
    #sel = HtmlXPathSelector(text=html)
    #r = sel.select(xpath)
    assert isinstance(root, lxml.html.HtmlElement), type(root)
    r = root.xpath(xpath)

    return "" if len(paths) == len(r) else "%s traversed structure VS %s matched by xpath" % (
                                                        len(paths), len(r))
    #assert len(paths) == len(r), "%s vs %s for %s" % (len(paths), len(r), xpath)
    #return xpath


"""
def best_xpath_from_xpaths(xpaths, html, paths):
    for xpath in xpaths:
        if not verify_xpath(xpath, html, paths):
            return xpath
    return None
"""

def xpath_for_es(es, root):
    #pprint(es)
    paths = map(lambda e: EInfo(e).parentpath_tuples(), es)
    #pprint(paths)
    xpath = xpath_by(paths)
    errstring = verify_xpath(xpath, root, paths)
    return xpath, errstring


def xpaths_for_es(es, text):
    pass


def main():
    HTMLFILE = "examples/frankonia.fr.html"
    PATHSFILE = "examples/frankonia.fr_paths.txt"

    html = open(HTMLFILE).read()
    paths = loads(open(PATHSFILE).read())
    paths = paths[0]
    xpath = xpath_by(paths)
    print xpath
    #print verify_xpath(xpath, html, paths)

    
if __name__ == "__main__":
    main()
    