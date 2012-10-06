# -*- coding: utf-8 -*-

from pprint import pprint, pformat

from utils import wget_root, map_list_list
from urls_utils import (grouped_hrefs_from_page_sets, is_grouped_hrefs_has_urls,
                        e_by_url_from_page, cmp_urls)
from xpath_utils import xpath_for_es
from htmlwipe import traversal, print_es, print_ess
from einfo import EInfo


class Site(object):
    # in
    name = None
    categories_url = None
    products_first_second_third = None
    # out
    next_products_xpath = None
    #
    debug = False
    
    def __init__(self, name, debug=False):
        self.name = name
        self.debug = debug
    
    def process(self):
        self.xpath_for_categories()
        self.xpath_for_products()
        if self.products_first_second_third:
            self.xpath_for_products_next()
        
    def report(self):
        print "="*30
        print "name: %s" % self.name
        print "categories_xpath: %s" % pformat(self.categories_xpath)
        #if self.products_ess:
        #    print_ess(self.products_ess, root=root)

        print "next_products_xpath: %s" % self.next_products_xpath
        print
        
    def xpath_for_categories(self):
        text, root = wget_root(self.categories_url)
        grouped_hrefs = grouped_hrefs_from_page_sets(root)
        grouped_hrefs = map_list_list(lambda x: x[-1], grouped_hrefs)
        #pprint(grouped_hrefs)
        grouped_hrefs = filter(lambda x: is_grouped_hrefs_has_urls(x,
                                                                   self.products),
                               grouped_hrefs)
        self.categories_xpath = map(lambda es: xpath_for_es(es, root),
                                    grouped_hrefs)
        
    def xpath_for_products(self):
        url = self.products[0]
        #print "url: ", url
        text, root = wget_root(url)
        ess = traversal(root, 1, min_elements=4,
              mintreeheight=3, maxtreeheight=4, maxmismatch=0.28)
        # TODO: grouping by level
        # TODO: finding xpath
        self.products_ess = ess
        print_ess(ess, root=root)

    def xpath_for_products_next(self):
        
        def is_only_url_in_es(url, es):
            return not bool(filter(lambda a: not cmp_urls(a.get("href"), url), es))
        
        first_url, second_url, third_url = self.products_first_second_third[0:3]
        _, first = wget_root(first_url)
        candidates = e_by_url_from_page(first, second_url)

        if self.debug:
            print "XPath raw candidates: ", pformat(candidates)
            #print "XPATHs"
            #pprint(map(lambda e: EInfo(e).search_for_xpath_ng(first, lambda z: True), candidates))
               
        candidates = map(lambda e: (e, EInfo(e).search_for_xpath_ng(first,
                                        lambda es: is_only_url_in_es(second_url, es)
                                        #lambda x: True
                                        )),
                         candidates)
        if self.debug:
            print "XPath first candidates: ", pformat(candidates)

        # reverify by second -> third_url
        _, second = wget_root(second_url)

        if self.debug:
            for e, xpaths in candidates:
                for xpath in xpaths:
                    print xpath
                    print third_url
                    es = second.xpath(xpath)
                    print_es(es)

        candidates = filter(lambda (e, xpaths):
               len(filter(
                          lambda xpath: is_only_url_in_es(third_url, second.xpath(xpath)),
                          xpaths))
               , candidates)
        #print "XPath last candidates: ", pformat(candidates)
        
        if candidates:
            self.next_products_xpath = candidates[0][1][0]


def main_multiple():
    """
    
    "poingdestres.co.uk"
    "bhphotovideo.com"
    "jbhifi.com.au"
    "harveynorman.com.au"
    "camerahouse.com.au"
    "teds.com.au"
    "digitalcamerawarehouse.com.au"
    "camskill.co.uk"
    "4x4tyres.co.uk"
    "tyredrive.co.uk"
    
    s = Site()
    s.name = ""
    s.categories_url = ""
    s.products = ["",
                    ""]
    s.products_first_second_third = ["",
                             "",
                             ""]
    sites.append(s)
    """

    sites = []
    
    # and 
    s = Site("euroffice.co.uk")
    s.categories_url = "http://www.euroffice.co.uk/Sitemap.aspx"
    s.products = ["http://www.euroffice.co.uk/g/n0l/Office-Supplies/Desktop-Stationery/Clips/",
                  "http://www.euroffice.co.uk/g/p1l/Office-Supplies/Filing-and-Archive/Binders/"]
    s.products_first_second_third = ["http://www.euroffice.co.uk/g/n0l/Office-Supplies/Desktop-Stationery/Clips/",
                           "http://www.euroffice.co.uk/g/n0l/Clips/?page=2&sort=BestSelling",
                           "http://www.euroffice.co.uk/g/n0l/Clips/?page=3&sort=BestSelling",]
    sites.append(s)

    s = Site("huntoffice.co.uk", debug=False)
    s.categories_url = "http://huntoffice.co.uk/"
    s.subcategories = ["http://huntoffice.co.uk/atlas-dictionary-photo-album.html",
                       "http://huntoffice.co.uk/mailroom-furniture.html",
                       "http://huntoffice.co.uk/folders-filing.html"]
    s.products = ["http://huntoffice.co.uk/card.html",
                  "http://www.euroffice.co.uk/g/p1l/Office-Supplies/Filing-and-Archive/Binders/"]
    s.products_first_second_third = ["http://huntoffice.co.uk/multifunctional-paper.html",
                           "http://huntoffice.co.uk/multifunctional-paper-p2.html",
                           "http://huntoffice.co.uk/multifunctional-paper-p3.html",]
    sites.append(s)

    s = Site("bristolangling.com")
    s.categories_url = "http://www.bristolangling.com"
    s.products = ["http://www.bristolangling.com/tackle.html", "http://www.bristolangling.com/bait.html"]
    s.products_first_second_third = ["http://www.bristolangling.com/tackle.html",
                           "http://www.bristolangling.com/tackle.html?p=2",
                           "http://www.bristolangling.com/tackle.html?p=3",
                           ]
    sites.append(s)
    
    """    
    # NOTE: probably recursive categories
    s = Site()
    s.name = "bristolangling.com"
    s.products = "http://www.chapmansangling.co.uk/shimano-coarse-reels_278.html"
    #sites.append(s)
    """
    
    s = Site("fostersofbirmingham.co.uk")
    s.categories_url = "http://www.fostersofbirmingham.co.uk/sitemap"
    s.products = ["http://www.fostersofbirmingham.co.uk/carp-and-barbel",
                    "http://www.fostersofbirmingham.co.uk/match-and-coarse"]
    s.products_first_second_third = ["http://www.fostersofbirmingham.co.uk/match-and-coarse",
                             "http://www.fostersofbirmingham.co.uk/match-and-coarse&Pg=2",
                             "http://www.fostersofbirmingham.co.uk/match-and-coarse&Pg=3"]
    sites.append(s)
    #s.process()
    #s.report()
    

    s = Site("tedcarter.co.uk")
    s.categories_url = "http://www.tedcarter.co.uk/"
    s.products = ["http://www.tedcarter.co.uk/browse/match-coarse/accessories/",
                    "http://www.tedcarter.co.uk/browse/fly-game/accessories/"]
    s.products_first_second_third = ["http://www.tedcarter.co.uk/browse/match-coarse/accessories/",
                             "http://www.tedcarter.co.uk/browse/match-coarse/accessories/&currentPage=2",
                             "http://www.tedcarter.co.uk/browse/match-coarse/accessories/&currentPage=3"]
    sites.append(s)
    #s.process()
    #s.report()

    
    s = Site("ericsangling.co.uk")
    s.categories_url = "http://www.ericsangling.co.uk/prods/index.html"
    s.products = ["http://www.ericsangling.co.uk/prods/pc96.html",
                    "http://www.ericsangling.co.uk/prods/pc110.html"]
    sites.append(s)

    """
    s = Site("summerlands-tackle.co.uk")
    s.categories_url = ""
    s.products = ["http://www.summerlands-tackle.co.uk/section.php/6431/1/abu-garcia-reels",
                    "http://www.summerlands-tackle.co.uk/section.php/6417/1/braid-and-mono-line"]
    s.products_first_second_third = ["",
                             "",
                             ""]
    sites.append(s)
    """

    """
    s = Site("climaxtackle.com")
    s.sitemap_url = "http://www.climaxtackle.com/sitemap.xml"
    s.products = ["",
                    ""]
    s.products_first_second_third = ["",
                             "",
                             ""]
    sites.append(s)
    """

    s = Site("tackleuk.co.uk")
    s.categories_url = "https://www.tackleuk.co.uk/#index/"
    s.products = ["https://www.tackleuk.co.uk/#index/cPath=26",
                    "https://www.tackleuk.co.uk/#index/cPath=104"]
    sites.append(s)

    s = Site("anglingdirect.co.uk")
    s.categories_url = "https://www.tackleuk.co.uk/#index/"
    s.products = ["http://www.anglingdirect.co.uk/store/carp/chairs",
                    "http://www.anglingdirect.co.uk/store/predator/terminal-tackle"]
    s.products_first_second_third = ["http://www.anglingdirect.co.uk/store/predator/terminal-tackle",
                             "http://www.anglingdirect.co.uk/store/predator/terminal-tackle?p=2",
                             "http://www.anglingdirect.co.uk/store/predator/terminal-tackle?p=3"]
    
    sites = sites[0:1]
    map(lambda s: s.process(), sites)
    map(lambda s: s.report(), sites)

if __name__ == "__main__":
    main_multiple()
    