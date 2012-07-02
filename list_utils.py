import itertools

def distance_between_sorted_arrays(a1, a2):
    """
    Artifishial metric.
    TODO: better use Levenstain
    """
    #end = False
    i1 = iter(a1)
    i2 = iter(a2)
    penalti = [0]

    f1 = [True]
    f2 = [True]
    
    def next1():
        try:
            return next(i1)
        except StopIteration:
            f1[0] = False
            raise
    
    def next2():
        try:
            return next(i2)
        except StopIteration:
            f2[0] = False
            raise
        
    def next12():
        try:
            e1 = next(i1)
        except StopIteration:
            f1[0] = False
        try:
            e2 = next(i2)
        except StopIteration:
            f2[0] = False
        if not (f1[0] and f2[0]):
            #penalti[0] += 1
            raise
        return e1, e2
    
    try:
        e1, e2 = next12()
        while True:
            if e1 == e2:
                e1, e2 = next12()
                #print e1, e2
            if e1 > e2:
                penalti[0] += 1
                e2 = next2()
            elif e2 > e1:
                penalti[0] += 1
                e1 = next1()            
    except StopIteration:
        #print f1, f2
        if not f1[0] and not f2[0]:
            pass
        elif f1[0]:
            penalti[0] += len(tuple(i1)) + 1
        elif f2[0]:
            penalti[0] += len(tuple(i2)) + 1
    return penalti[0]



def test():
    a1 = [1, 3, 5]
    a2 = [1, 3, 6]
    a3 = [1, 3, 5, 10]
    a4 = [1, 2, 3, 5]
    a5 = [1, 2, 3, 5, 6]
    a6 = [1, 2, 3, 5, 6, 7, 8]
    a7 = [2, 4 ,6]
    assert distance_between_sorted_arrays(a1, a1) == 0
    print distance_between_sorted_arrays(a1, a2)
    print distance_between_sorted_arrays(a1, a3)
    assert distance_between_sorted_arrays(a1, a3) == 1
    print distance_between_sorted_arrays(a1, a4)
    assert distance_between_sorted_arrays(a1, a4) == 1
    print distance_between_sorted_arrays(a1, a5)
    print distance_between_sorted_arrays(a1, a6)
    assert distance_between_sorted_arrays(a1, a5) == 2
    assert distance_between_sorted_arrays(a1, a6) == 4
    print distance_between_sorted_arrays(a1, a7)


if __name__ == "__main__":
    test()

