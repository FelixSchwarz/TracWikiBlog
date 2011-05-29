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

import unittest

from BeautifulSoup import BeautifulSoup
from trac.attachment import Attachment
from trac.test import EnvironmentStub, Mock
from trac.versioncontrol.api import RepositoryManager
from trac.wiki.model import WikiPage
from trac_dev_platform.test import EnvironmentStub, TracTest
from trac_dev_platform.test.lib.pythonic_testcase import *

from trac_wiki_blog.macro import ShowPostsMacro


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
    
    def _test_has_page_to_create_a_new_blog_post(self):
        self.grant_permission('anonymous', 'TRAC_ADMIN')
        self._get_newblogpost()
    
    def _test_has_correct_title(self):
        self.grant_permission('anonymous', 'TRAC_ADMIN')
        
        soup = self._get_newblogpost_dom()
        page_title = soup.find(name='title')
        assert_equals(u'Create New Blog Post \u2013 My Project', page_title.text.replace('\n', '').replace('\t', ''))
        
        wiki_content = soup.find(name='div', attrs={'id': 'content', 'class': 'wiki'})
        heading = wiki_content.find('h1')
        assert_equals('Create New Blog Post', heading.text)
    
    def _test_has_only_one_field_for_blog_title(self):
        # This is a test case for the dreaded "item duplication" problem in
        # Genshi 0.5.1 (http://genshi.edgewall.org/ticket/254)
        self.grant_permission('anonymous', 'TRAC_ADMIN')
        soup = self._get_newblogpost_dom()
        
        wiki_content = soup.find(name='div', attrs={'id': 'content', 'class': 'wiki'})
        title_fields = wiki_content.findAll(name='input', attrs={'name': 'blogtitle'})
        assert_length(1, title_fields)
    
    def _test_sends_form_submission_to_the_same_url_as_the_initial_request(self):
        self.grant_permission('anonymous', 'TRAC_ADMIN')
        soup = self._get_newblogpost_dom()
        form = soup.find(name='form', attrs={'id': 'edit', 'method': 'post'})
        assert_equals('', form['action'])
        
    # TODO: Check: Tag interface
    # TODO: Check that the newblogpost page is only accessible for WIKI_MODIFY+TAGS_MODIFY
    # --------------------------------------------------------------------------
    # creating a new post
    
    def test_can_submit_a_new_blog_post(self):
        self.grant_permission('anonymous', 'TRAC_ADMIN')
        # TODO: Posting without version -> 500 in Trac
        req = self.post_request('/newblogpost', action='edit', save='Submit changes', blogtitle='title', text='some post', tags='blog', version=0)
        response = self.simulate_request(req)
        assert_equals(303, response.code())
        
        page = WikiPage(self.env, '2011/04/title')
        assert_true(page.exists)
        assert_equals('= title =\n\nsome post', page.text)
    
    # --------------------------------------------------------------------------
    # nav item
    
    def _newpost_link(self, path='/about'):
        # necessary so the /about path works. That's a good path because every 
        # user can access the page.
        import trac.about
        response = self.simulate_request(self.get_request(path))
        soup = BeautifulSoup(response.html())
        newpost_link = soup.find('a', attrs={'href': '/newblogpost'})
        return newpost_link
    
    def assert_newpost_link_is_displayed(self):
        newpost_link = self._newpost_link()
        assert_not_none(newpost_link)
        return newpost_link
    
    def assert_newpost_link_is_not_displayed(self):
        newpost_link = self._newpost_link()
        assert_none(newpost_link)
    
    def _test_shows_link_to_new_blog_post_page_in_nav_bar(self):
        self.grant_permission('anonymous', 'TRAC_ADMIN')
        
        newpost_link = self.assert_newpost_link_is_displayed()
        assert_equals('New Blog Post', newpost_link.text)
    
    def _test_shows_highlighted_link_when_on_the_newblogpost_page(self):
        self.grant_permission('anonymous', 'TRAC_ADMIN')
        # if there are any warnings because of a non-existing repository, Trac
        # will not highlight any navigation item
        self.disable_component(RepositoryManager)
        
        newpost_link = self._newpost_link('/newblogpost')
        nav_item = newpost_link.parent
        assert_equals('active', nav_item.get('class'))
    
    def _test_only_show_newblogpost_link_if_user_has_enough_permissions(self):
        self.assert_has_permission('anonymous', 'WIKI_VIEW')
        
        self.grant_permission('anonymous', 'TAGS_MODIFY')
        self.assert_has_permission('anonymous', 'TAGS_MODIFY')
        self.assert_has_no_permission('anonymous', 'WIKI_CREATE')
        self.assert_newpost_link_is_not_displayed()

        self.revoke_permission('anonymous', 'TAGS_MODIFY')
        self.grant_permission('anonymous', 'WIKI_CREATE')
        self.assert_has_no_permission('anonymous', 'TAGS_MODIFY')
        self.assert_has_permission('anonymous', 'WIKI_CREATE')
        self.assert_newpost_link_is_not_displayed()

        self.grant_permission('anonymous', 'TAGS_MODIFY')
        self.assert_has_permission('anonymous', 'TAGS_MODIFY')
        self.assert_has_permission('anonymous', 'WIKI_CREATE')
        self.assert_newpost_link_is_displayed()

#class TestNewBlogPostWithPreview(FunctionalTwillTestCaseSetup):
# check that preview page is visible
# check that all data is still there (summary, content, tags)
# check that you can submit the page

# check warning if title is empty
# check that blog tag is set automatically

