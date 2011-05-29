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

from cStringIO import StringIO
import re
import unittest

from BeautifulSoup import BeautifulSoup
from trac.attachment import Attachment
from trac.test import EnvironmentStub, Mock
from trac.wiki.model import WikiPage
from trac_dev_platform.test import EnvironmentStub, mock_request, TracTest
from trac_dev_platform.test.lib.pythonic_testcase import *

from trac_wiki_blog.macro import ShowPostsMacro

from post_finder_test import create_tagged_page


class ShowPostsMacroTest(unittest.TestCase):

    def setUp(self):
        self.env = EnvironmentStub(default_data=True, enable=('trac_wiki_blog.*', 'tractags.*', 'trac.*'))
        self.env.upgrade()
        self.macro = ShowPostsMacro(self.env)
    
    def tearDown(self):
        self.env.destroy_temp_directory()
    
    def req(self):
        req = mock_request('/')
        req.populate(self.env)
        return req
    
    def _expand_macro(self, argument_string=''):
        formatter = Mock(req=self.req())
        html = self.macro.expand_macro(formatter, 'ShowPosts', argument_string)
        return html
    
    # --------------------------------------------------------------------------
    # Macro Title
    
    def _title_from_html(self, html):
        soup = BeautifulSoup(html)
        title_element = soup.find(name='h1', attrs={'class': 'blog_heading'})
        return title_element.string
    
    def test_has_default_title(self):
        title = self._title_from_html(self._expand_macro())
        assert_equals('Blog Posts', title)
    
    def test_can_set_custom_title(self):
        title = self._title_from_html(self._expand_macro(u'title=Latest…'))
        assert_equals(u'Latest…', title)
    
    def test_strips_spaces_from_macro_title(self):
        title = self._title_from_html(self._expand_macro(u'title= A Title '))
        assert_equals(u'A Title', title)

    # --------------------------------------------------------------------------
    # Relative attachment links
    
    def _has_permission(self, username, action):
        from trac.perm import DefaultPermissionPolicy, PermissionSystem
        DefaultPermissionPolicy(self.env).permission_cache = {}
        return action in PermissionSystem(self.env).get_user_permissions(username)
    
    def _grant_permission(self, username, action):
        from trac.perm import DefaultPermissionPolicy, PermissionSystem
        if self._has_permission(username, action):
            return
        DefaultPermissionPolicy(self.env).permission_cache = {}
        PermissionSystem(self.env).grant_permission(username, action)
        assert self._has_permission(username, action)
    
    def _add_attachment(self, parent_resource, filename):
        attachment = Attachment(self.env, parent_resource.child('attachment', None))
        attachment_fp = StringIO('some content')
        attachment.insert(filename, attachment_fp, len(attachment_fp.getvalue()))
        return attachment
    
    def test_can_resolve_relative_attachment_links_correclty(self):
        self.env.use_temp_directory()
        # Need to import so that WIKI_* permissions are known
        from trac.wiki.web_ui import WikiModule
        self._grant_permission('anonymous', 'TRAC_ADMIN')
        
        page = create_tagged_page(self.env, self.req(), 'Foo', '= Foo =\n[attachment:test.txt]', ('blog',))
        page.save(None, None, '127.0.0.1')
        self._add_attachment(page.resource, 'test.txt')

        html = self._expand_macro()
        attachment_link = BeautifulSoup(html).find(name='a', text='test.txt').parent
        assert_equals('attachment', attachment_link['class'])

    # --------------------------------------------------------------------------
    # Blog Post Titles
    
    def test_title_is_only_shown_once(self):
        self._grant_permission('anonymous', 'TRAC_ADMIN')
        page = create_tagged_page(self.env, self.req(), 'Foo', '= SomeTitle =\ncontent', ('blog',))
        page.save(None, None, '127.0.0.1')
        
        soup = BeautifulSoup(self._expand_macro())
        plain_text = ''.join(soup.div(text=True))
        # looking in plain text (with all tags stripped) as Trac will add the 
        # title also in the dom node id and an anchor to link to that heading
        matches = re.findall('SomeTitle', plain_text)
        assert_length(1, matches)
    
    def test_can_use_wiki_text_in_page_title(self):
        self._grant_permission('anonymous', 'TRAC_ADMIN')
        page = create_tagged_page(self.env, self.req(), 'Foo', "= Some ''italic'' Title =\ncontent", ('blog',))
        page.save(None, None, '127.0.0.1')
        
        title_link = BeautifulSoup(self._expand_macro()).find('a', href='/wiki/Foo')
        assert_contains('Some <i>italic</i> Title', unicode(title_link))
    
    def test_post_title_contains_link_to_blog_post_page(self):
        self._grant_permission('anonymous', 'TRAC_ADMIN')
        page = create_tagged_page(self.env, self.req(), 'Foo', "= Some Title =\ncontent", ('blog',))
        page.save(None, None, '127.0.0.1')
        
        html = self._expand_macro()
        post_heading = BeautifulSoup(html).find('h1', id='SomeTitle')
        post_link = post_heading.find('a', href='/wiki/Foo')
        assert_not_none(post_link)
        assert_equals('Some Title', post_link.text)
        # Section linking is a JS feature so we can't test it here…

