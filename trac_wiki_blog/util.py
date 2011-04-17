# -*- coding: utf-8 -*-
#
# The MIT License
# 
# Copyright (c) 2008-2011 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Authors:
#   - Felix Schwarz
#   - Martin Häcker
#
# With ideas and initial code from John Hampton <pacopablo@pacopablo.com> and
# his TracBlogPlugin (http://trac-hacks.org/wiki/TracBlogPlugin)

import datetime
import re

from trac.wiki.model import WikiPage
from trac.util.datefmt import utc

from tractags.api import TagSystem

__all__ = ['content_from_wiki_markup', 'title_from_wiki_markup',
           'wiki_pagename_from_title', 'get_wiki_pagename', 
           'sort_by_creation_date', 'creation_date_of_page', 
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

def creation_date_of_page(page):
    page = WikiPage(page.env, page.name, 1)
    return page.time

def load_pages_with_tags(env, req, tags):
    tag_system = TagSystem(env)
    pages = []
    blog_resources = [i for i in tag_system.query(req, tags)]
    for resource, ignored in blog_resources:
        pages.append(WikiPage(env, resource))
    return pages

def paginate_page_list(page_list, start_index=0, how_many=10):
    return page_list[start_index:how_many]


