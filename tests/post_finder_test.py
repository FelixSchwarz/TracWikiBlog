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
import random
import unittest

from trac.util.datefmt import utc
from trac.test import Mock, EnvironmentStub, MockPerm
from trac.web.href import Href
from trac.wiki.model import WikiPage
from tractags.api import TagSystem

from trac_wiki_blog.lib.pythonic_testcase import *
from trac_wiki_blog.util import creation_date_of_page, load_pages_with_tags, \
    sort_by_creation_date, paginate_page_list


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

def create_tagged_page(env, req, name, text, tags):
    page = WikiPage(env, name, None)
    page.text = text
    tag_system = TagSystem(env)
    tag_system.add_tags(req, page.resource, tags)
    return page


class PostFinderTest(unittest.TestCase):
    
    def setUp(self):
        self.env = EnvironmentStub(default_data=True, enable=["tractags.*", 'trac.*'])
        self.env.upgrade()
        self.env.db.commit()
        self.req = Mock(perm=MockPerm(), args={}, href=Href('/'))
    
    def test_can_save_and_load_wiki_page(self):
        page = WikiPage(self.env, "Foo", None)
        page.text = "barfoo"
        page.save("fnord", "bar", "localhost")
        
        assert_equals("barfoo", WikiPage(self.env, "Foo", None).text)
    
    def test_can_add_tags_and_retrieve_tagged_pages(self):
        page = create_tagged_page(self.env, self.req, "pagename", "pagetext", ["blog"])
        page.save("author", "comment", "remote_address")
        assert_equals("pagetext", WikiPage(self.env, "pagename", None).text)
        
        pages = load_pages_with_tags(self.env, self.req, "blog")
        assert_equals(1, len(pages))
        page = pages[0]
        assert_equals("pagetext", page.text)
    
    def test_can_get_page_creation_date(self):
        long_ago = datetime.datetime(year=2000, month=1, day=1, tzinfo=utc)
        page = create_tagged_page(self.env, self.req, "name", "text", ["blog"])
        page.save("author", "comment", "remote_address", long_ago)
        page.text = "version 2"
        page.save("author", "comment", "remote_address")
        
        page = WikiPage(self.env, "name", None)
        assert_equals("version 2", page.text)
        assert_not_equals(long_ago, page.time)
        assert_equals(long_ago, creation_date_of_page(page))
    
    def test_can_sort_page_list(self):
        pagelist = create_tagged_pages(self.env, self.req, ["fnord"], 4)
        pagelist.reverse()
        sorted_list = pagelist[:]
        assert_equals(sorted_list, pagelist)
        random.shuffle(pagelist)
        assert_not_equals(sorted_list, pagelist)
        pagelist = sort_by_creation_date(pagelist)
        assert_equals(sorted_list, pagelist)
    
    def test_can_get_paginated_page_list(self):
        page_list = create_tagged_pages(self.env, self.req, ["fnord"], 4)
        assert_equals(page_list[0:2], paginate_page_list(page_list, 0, 2))


