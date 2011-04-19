# -*- coding: utf-8 -*-
#
# The MIT License
# 
# Copyright (c) 2011 Felix Schwarz <felix.schwarz@oss.schwarz.eu>
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

import unittest

from BeautifulSoup import BeautifulSoup
from trac.attachment import Attachment
from trac.test import EnvironmentStub, Mock
from trac.wiki.model import WikiPage

from trac_wiki_blog.lib.pythonic_testcase import *
from trac_wiki_blog.macro import ShowPostsMacro

from show_posts_macro_test import EnvironmentStub, mock_request
from test_util import TracTest

class NewBlogPostTest(TracTest):

    def setUp(self):
        self.env = EnvironmentStub(default_data=True, enable=('trac_wiki_blog.*', 'tractags.*', 'trac.*'))
        self.env.upgrade()
    
    def tearDown(self):
        self.env.destroy_temp_directory()
    
    # --------------------------------------------------------------------------
    # checking the /newblogpost page+template
    
    def _get_newblogpost(self):
        req = self.get_request('/newblogpost')
        response = self.simulate_request(req)
        assert_equals(200, response.code())
        return response
    
    def _get_newblogpost_dom(self):
        response = self._get_newblogpost()
        return BeautifulSoup(response.html())
    
    def test_has_page_to_create_a_new_blog_post(self):
        self.grant_permission('anonymous', 'TRAC_ADMIN')
        self._get_newblogpost()
    
    def test_has_correct_title(self):
        self.grant_permission('anonymous', 'TRAC_ADMIN')
        
        soup = self._get_newblogpost_dom()
        page_title = soup.find(name='title')
        assert_equals(u'Create New Blog Post \u2013 My Project', page_title.text.replace('\n', '').replace('\t', ''))
        
        wiki_content = soup.find(name='div', attrs={'id': 'content', 'class': 'wiki'})
        heading = wiki_content.find('h1')
        assert_equals('Create New Blog Post', heading.text)
    
    def test_has_only_one_field_for_blog_title(self):
        # This is a test case for the dreaded "item duplication" problem in
        # Genshi 0.5.1 (http://genshi.edgewall.org/ticket/254)
        self.grant_permission('anonymous', 'TRAC_ADMIN')
        soup = self._get_newblogpost_dom()
        
        wiki_content = soup.find(name='div', attrs={'id': 'content', 'class': 'wiki'})
        title_fields = wiki_content.findAll(name='input', attrs={'name': 'blogtitle'})
        assert_length(1, title_fields)

# TODO: Check: Tag interface
# TODO: Check form URL
# TODO: Check that the newblogpost page is only accessible for WIKI_MODIFY+TAGS_MODIFY

