import itertools
from pprint import pprint, pformat

from lxml import etree
import lxml.html

from tree_utils import print_tree
from utils import uniq_list_with_order


class EInfo():
    
    def __init__(self, e):
        assert not isinstance(e, list)
        self.e = e
    
    def __repr__(self):
        #return repr(self.e)
        #return str()
        print_tree(self.e)
    
    def info(self):
        self.urls = map(lambda x: (x, x.get("href")), self.e.findall(".//a"))
        self.imgs = map(lambda x: (x, x.get("src")), self.e.findall(".//img"))
        self.text = filter(lambda x: x[1], map(lambda x: (x, x.text_content()), self.e.findall(".//*")))
        return {'urls': self.urls,
                'imgs': self.imgs,
                'text': self.text}

    def find(self, s):
        "very simple PoF"
        ret = []
        for e in self.e.iterdescendants():
            for v in e.values():
                if s in v:
                    ret.append(e)
        return ret

    def parentpath(self, root=None, with_root=False):
        e = self.e
        do = True
        ret = []
        while do:
            ret.insert(0, e)
            e = e.getparent()
            if not e:
                do = False
            elif e == root:
                if with_root:
                    ret.insert(0, root)
                do = False
        return ret

    def childpath(self, e):
        childpath = EInfo(e).parentpath(root=self.e)
        return childpath

    def parentpath_str(self, root=None, separator=" -> "):
        ret = self.parentpath(root=root)
        return separator.join(
                map(lambda x: "%s(%s)" % (x.tag, x.attrib), ret))

    def parentpath_tuples(self, root=None):
        ret = self.parentpath(root=root)
        return map(lambda x: (x.tag, x.items()), ret)
    
    def get_exact_xpath(self, root):
        assert isinstance(root, lxml.html.HtmlElement)
        tree = etree.ElementTree(root)
        return tree.getpath(self.e)

    def xpath_gen_ununiq(self, root=None, related=False):
        if root:
            yield self.get_exact_xpath(root)
        all_attribs = ['id', 'class', 'title', 'text()']
        for attribs_n in range(len(all_attribs), 0, -1):
            for without_last_n_attribs in range(2):
                for attribs in list(itertools.combinations(all_attribs, attribs_n)):
                    #print attribs
                    #yield self.create_xpath(root=root, without_last_n_attribs=without_last_n_attribs)
                    yield self.create_xpath(root=root, related=related,
                                        attribs=attribs, without_last_n_attribs=without_last_n_attribs)
        yield self.create_xpath(root=root, related=related, with_attribs=False)

    def xpath_gen(self, root=None, related=False):
        "order matter"
        xpaths = list(self.xpath_gen_ununiq(root=root, related=related))
        xpaths = uniq_list_with_order(xpaths)
        return xpaths
    
    def search_for_xpath(self, root, nmatch, relroot=None):
        ret = []
        for xpath in self.xpath_gen(root=relroot):
            n = len(root.xpath(xpath))
            if n == nmatch:
                return xpath, None
            ret.append((xpath, n))
        return None, ret

    def search_for_xpath_ng(self, root, func, related=False):
        ret = []
        xpaths = self.xpath_gen(root=root, related=related)
        #print "xpaths", pformat(xpaths)
        for xpath in xpaths:
            #print "xpath: ", xpath
            es_back = root.xpath(xpath)
            if func(es_back):
                ret.append(xpath)
        return ret

    def create_xpath(self, root=None, related=False,
                 with_attribs=True, attribs=[],
                 preffered_attribs=["id", "class"], without_last_n_attribs=0,
                 debug=False):
        path = self.parentpath(root=root, with_root=not related)
        ret = []
        for e in path:
            atrs = []
            if with_attribs and e.keys():
                if attribs:
                    for k in attribs:
                        v = e.get(k)
                        if e.tag == "a" and k == "text()":
                            v = e.text
                            if not v or not v.strip() or len(v.split("\n")) > 1 or "'" in v:
                                continue
                            if debug:
                                print "text: %s" % v
                            atrs.append((k, v))
                            continue
                        if k not in e.keys():
                            continue
                        atrs.append((k, v))
                else:
                    keys = e.keys()
                    for k in preffered_attribs:
                        if k in keys:
                            keys.remove(k)
                    for k in preffered_attribs + keys:
                        if k not in e.keys():
                            continue
                        v = e.get(k)
                        atrs.append((k, v))
                        break
            ret.append((e.tag, atrs))
        if debug:
            print "ret:", pformat(ret)
        if without_last_n_attribs:
            _without_last_n_attribs = min(without_last_n_attribs, len(ret))
            for i in range(len(ret) - without_last_n_attribs, len(ret)):
                ret[i] = (ret[i][0], [])
        #ret.append("{}[@{}='{}']".format(e.tag, k, v))    
        ret = map(lambda x: x[0] if not x[1] else "{}[{}]".format(x[0], 
                                    ' and '.join(map(lambda y: "@{}='{}'".format(y[0], y[1]), x[1]))
                                                              ) , ret)
        xpath = ("./" if related else "/") + "/".join(ret)
        if debug:
            print "xpath:", xpath
        return xpath
    
    
def test():
    #FILE = "htmls/frankonia.fr.html"
    FILE = "examples/naturabuy.fr.html"
    #FILE = "htmls/cariboom.com.html"
    #FILE = "htmls/Veniard Esmond Dury Trebles Nickel Plated   Ted Carter Fishing Tackle.html"
    text = open(FILE).read()
    root = lxml.html.document_fromstring(text)
    e = root.xpath("//a")[0]
    #print EInfo(e).create_xpath()
    pprint(list(EInfo(e).xpath_gen()))
    
if __name__ == "__main__":
    test()
    