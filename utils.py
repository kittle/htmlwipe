import urllib2

import lxml.html

wget_cache = {}


def wget(url):
    #print "url: %s" % url
    if wget_cache.has_key(url):
        return wget_cache.get(url)
    f = urllib2.urlopen(url)
    data = f.read()
    wget_cache[url] = data
    return data


def wget_root(url):
    text = wget(url)
    return text, lxml.html.document_fromstring(text)


def map_u(functor, applier, l):
    return applier(functor, l)


def map_list_list(functor, l):
    return map(lambda x: map(functor, x), l)


def map_list_list_list(functor, l):
    return map(lambda x: map(lambda y: map(functor, y), x), l)


def reduce_list_nesting(p):
    ret = []
    for p1 in p:
        for p2 in p1:
            ret.append(p2)
    return ret


def uniq_list_with_order(l):
    "TODO: speedup"
    ret = []
    #map(lambda (k, v): (k, len(list(v))), itertools.groupby(sorted(l)))
    for i in l:
        if i in ret:
            continue
        ret.append(i)
    return ret
    