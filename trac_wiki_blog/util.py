import datetime
import re

from trac.wiki.model import WikiPage
from trac.util.datefmt import utc

from tractags.api import TagSystem

__all__ = ['content_from_wiki_markup', 'title_from_wiki_markup',
           'wiki_pagename_from_title', 'get_wiki_pagename', 
           'sort_by_creation_date', 'create_tagged_pages',
           'creation_date_of_page', 'create_tagged_page', 
           'load_pages_with_tags']

# ===============================================================
# Parsing

parsing_regex = re.compile(r'.*?^\s*=+\s+([^\n\r]+?)\s+=+\s*(.*?$.*)',
                                re.MULTILINE|re.DOTALL)

def content_from_wiki_markup(wiki_markup):
    match = parsing_regex.match(wiki_markup)
    if match is None:
        raise ValueError('Markup is missing a title: %s' % wiki_markup)
    return match.group(2)

def title_from_wiki_markup(wiki_markup):
    match = parsing_regex.match(wiki_markup)
    if match is None:
        raise ValueError('Markup is missing a title: %s' % wiki_markup)
    return match.group(1)

# TODO: Better name - this is not the wiki pagename but only the 'suffix' 
def wiki_pagename_from_title(title):
    basetitle = title.strip().lower()
    basetitle = basetitle.replace(' ', '-')
    return basetitle


def get_wiki_pagename(creation_date, title):
    basename = wiki_pagename_from_title(title)
    return '%d/%02d/%s' % (creation_date.year, creation_date.month, basename)

# ===============================================================
# Getting Pages

def sort_by_creation_date(pagelist):
    pagelist_with_dates = zip(map(creation_date_of_page, pagelist), pagelist)
    pagelist_with_dates.sort()
    pagelist_with_dates.reverse()
    return [i[1] for i in pagelist_with_dates]

def create_tagged_pages(env, req, tags, number_of_pages):
    long_ago = datetime.datetime(year=2000, month=1, day=1, tzinfo=utc)
    one_day = datetime.timedelta(days=1)
    pagelist = []
    for i in range(number_of_pages):
        name = 'page ' + str(i)
        text = 'pagetext ' + str(i)
        page = create_tagged_page(env, req, name, text, tags)
        long_ago += one_day
        page.save('author', 'comment', 'remote', long_ago)
        page = WikiPage(env, name, None)
        pagelist.append(page)
    return pagelist

def creation_date_of_page(page):
    page = WikiPage(page.env, page.name, 1)
    return page.time

def create_tagged_page(env, req, name, text, tags):
    page = WikiPage(env, name, None)
    page.text = text
    tag_system = TagSystem(env)
    tag_system.add_tags(req, page.resource, tags)
    return page

def load_pages_with_tags(env, req, tags):
    tag_system = TagSystem(env)
    pages = []
    blog_resources = [i for i in tag_system.query(req, tags)]
    for resource, ignored in blog_resources:
        pages.append(WikiPage(env, resource))
    return pages

def paginate_page_list(page_list, start_index=0, how_many=10):
    return page_list[start_index:how_many]