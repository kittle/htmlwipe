from Queue import Queue


def traverse_deep_(e, level, todo=lambda x: x, maxlevel=None):
    res = []
    res.append((level, todo(e)))
    for ch in e.getchildren():
        #print ch
        #if maxlevel and level > maxlevel:
        #    continue
        res.extend(
            traverse_deep_(ch, level+1, todo=todo, maxlevel=maxlevel))
    #print "level: ", level, res
    return res


def traverse_deep(root, todo=lambda x: x, initlevel=1, maxlevel=None):
    return traverse_deep_(root, initlevel, todo=todo, maxlevel=maxlevel)


def traverse_wide(root, todo=lambda x: x, initlevel=1, maxlevel=None,
                  minlevel=0):
    res = []
    q = Queue()
    q.put((initlevel, root))
    maxl = initlevel
    while not q.empty():
        level, x = q.get()
        maxl = max(maxl, level)
        res.append(todo(x))
        if maxlevel and level + 1 > maxlevel:
            continue
        for ch in x.iterchildren():
            q.put((level+1, ch))
    if maxl > minlevel:
        return res
    else:
        return None
    

def str_element(e):
    attrib = " ".join(['%s="%s"' % (k,v) for k,v in e.attrib.items()])
    return "<%s%s>%s%s" % (e.tag, " " + attrib if attrib else "",
                             " " + e.label.strip() if e.label and e.label.strip() else "",
                             " " + e.text.strip() if e.text and e.text .strip() else "" )


def print_special(spec):
    for level, e in spec:
        print "  "*(level-1), e


def print_tree(root):
    print_special(traverse_deep(root, todo=str_element))
    