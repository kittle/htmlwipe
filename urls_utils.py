from pprint import pprint
from StringIO import StringIO
import glob
import itertools
import sys
from collections import defaultdict
import urlparse
import htmllib

import lxml.html

from levenshtein import levenshtein
from einfo import EInfo
from xpath_utils import create_xpath
from utils import reduce_list_nesting, map_list_list


def tree(): return defaultdict(tree)


def dicts(t, v=lambda x: x):
    #return {k: dicts(t[k]) for k in t}
    return {v(k): dicts(t[k], v=v) for k in t}


def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()


def cmp_urls(url1, url2):
    if not url1 or not url2:
        return url1 == url2
    #print "urlcmp: %s %s" % (url1, url2)
    assert isinstance(url1, str), type(url1)
    assert isinstance(url2, str), type(url2)
    u1 = urlparse.urlsplit(unescape(url1))
    u2 = urlparse.urlsplit(unescape(url2))
    if u1[0] and u2[0]:
        return url1 == url2
    else:
        return u1[2:] == u2[2:]


def is_url_in_urls(url, urls):
    assert isinstance(urls, list)
    for u in urls:
        if cmp_urls(url, u):
            return True
    return False


def grouping_sorted_paths_by_xpath(paths):
    #pprint(paths)
    f = lambda e: EInfo(e[-1]).create_xpath(with_attribs=False)
    paths_by_xpath = sorted(paths, key=f)
    p = itertools.groupby(paths_by_xpath, key=f)
    p = map(lambda (k, i): list(i), p)
    return p


def grouping_list_by_levenstein(urls, key=lambda x: x):
    ret = []
    prev = None
    urls = sorted(urls, key=key)
    lret = []
    for url in urls:
        if prev:
            if levenshtein(key(prev), key(url)) == 1:
                if not lret:
                    lret.append(prev)
                lret.append(url)
            else:
                if lret:
                    ret.append(lret)
                    lret = []
                    #urls.insert(0, url)
        prev = url
    else:
        if lret:
            ret.append(lret)
    return ret


def is_grouped_hrefs_has_urls(grouped_hrefs, urls):
    href_urls = map(lambda x: x.get("href"), grouped_hrefs)
    for url in urls:
        if not is_url_in_urls(url, href_urls):
            return False
    return True


def e_with_url_from_root(root, xpath="//a"):
    if xpath != "//a":
        raise RuntimeError("old code")
    return root.xpath("//a")


def grouped_hrefs_from_page_sets(root, xpath="//a"):

    #es = root.xpath(xpath)
    es = e_with_url_from_root(root, xpath=xpath)
    
    paths = [EInfo(e).parentpath() for e in es]

    # grouping_by_pathlen
    paths_by_length = sorted(paths, key=len)
    p = itertools.groupby(paths_by_length, key=len)
    p = map(lambda (k, i): list(i), p)
    #pprint(p)
    
    p = map(grouping_sorted_paths_by_xpath, p)

    href_sets = reduce_list_nesting(p)
    return href_sets


def grouped_hrefs_from_page(root, xpath="//a", max_urls_out=10):

    href_sets = grouped_hrefs_from_page_sets(root, xpath=xpath)
    ret = map(lambda e: {
                         'len': len(e),
                         'xpath': EInfo(e[0][-1]).search_for_xpath(root, len(e))[0],
                         'urls': map(lambda x: (x[-1].get('href'), x[-1].text), e)[:max_urls_out]},
                                                        href_sets)
    ret = sorted(ret, key=lambda x:x['len'], reverse=True)

    # verify back xpath and add len_by_xpath
    map(lambda e: e.update(len_by_xpath=len(root.xpath(e['xpath'])) if e['xpath'] else None), ret)
    
    return ret, href_sets


def e_by_url_from_page(root, url):
    #return root.xpath("//a[@href='%s']" % url)
    return filter(lambda a: cmp_urls(a.get("href"), url), root.xpath("//a"))


def looking_for_next_page(root, href_sets):
    ret = {}
    ret['urls_with_next_somehow'] = grouped_hrefs_from_page(root,
        xpath = "//a[contains(@id, 'next')] | //a[contains(@class, 'next')] | //a[contains(text(), 'Next')] | //a[contains(text(), 'next')] ")
    # add url
    r = map(
                    lambda x: map(
                                    lambda y: [y[-1], y[-1].get("href")], x)
            , href_sets)
    r = map(
              lambda x: grouping_list_by_levenstein(x,
                                                    key=lambda y: y[1]
                                )
              , r)
    r = filter(None, r)
    r = reduce_list_nesting(r)
    map_list_list(lambda x:x.append(EInfo(x[0]).create_xpath()), r)
    ret['urls_grouped_by_levei'] = r
    return ret

    
def main_filename(filename):
    text = open(filename).read()
    return main_html(text)


def main_html(text):
    data = {}
    #root = lxml.html.parse(filename).getroot()
    html = lxml.html.parse(StringIO(text))
    root = html.getroot()
    hrefs_info, href_sets = grouped_hrefs_from_page(root)
    data['urls_grouped'] = hrefs_info
    data['urls_next_somehow'] = looking_for_next_page(root, href_sets)
    pprint(data)


def main():
    main_filename("examples/euroffice.co.uk-sitemap.html")
    return
    for filename in glob.glob("examples/*.html"):
        main_filename(filename)
        print


def test_tree():
    t = tree()
    t['a']['b']['c']
    t['a']['b']['d']
    t['a']['e']
    pprint(dicts(t))
    #pprint(dicts(t, v=lambda x :id(x)))


if __name__ == "__main__":
    #test_tree()

    if len(sys.argv) > 1:
        if sys.argv[1] == '-':
            text = sys.stdin.read()
            main_html(text)
        else:
            main_filename(sys.argv[1])
    else:
        main()
