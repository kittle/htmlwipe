
from json import loads
from pprint import pprint

from scrapy.selector import XPathSelector, XmlXPathSelector, HtmlXPathSelector


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

def verify_xpath(xpath, html, paths):
    sel = HtmlXPathSelector(text=html)
    r = sel.select(xpath)
    return "" if len(paths) == len(r) else "%s traversed structure VS %s matched by xpath" % (
                                                        len(paths), len(r))
    #assert len(paths) == len(r), "%s vs %s for %s" % (len(paths), len(r), xpath)
    #return xpath


def main():
    HTMLFILE = "examples/frankonia.fr.html"
    PATHSFILE = "examples/frankonia.fr_paths.txt"

    html = open(HTMLFILE).read()
    paths = loads(open(PATHSFILE).read())
    paths = paths[0]
    xpath = xpath_by(paths)
    print xpath
    print verify_xpath(xpath, html, paths)

    
if __name__ == "__main__":
    main()
    