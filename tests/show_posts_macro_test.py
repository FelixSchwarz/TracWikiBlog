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

import re
import unittest

from BeautifulSoup import BeautifulSoup
from trac.attachment import Attachment
from trac.test import EnvironmentStub, Mock
from trac.wiki.model import WikiPage

from trac_wiki_blog.lib.pythonic_testcase import *
from trac_wiki_blog.macro import ShowPostsMacro

from post_finder_test import create_tagged_page

# ------------------------------------------------------------------------------
from cStringIO import StringIO
import re

from trac.web.api import Request, RequestDone
from trac.web.chrome import Chrome

class MockResponse(object):
    
    def __init__(self):
        self.status_line = None
        self.headers = []
        self.body = StringIO()
    
    def code(self):
        string_code = self.status_line.split(' ', 1)[0]
        return int(string_code)
    
    def start_response(self, status, response_headers):
        self.status_line = status
        self.headers = response_headers
        return lambda data: self.body.write(data)
    
    def html(self):
        self.body.seek(0)
        body_content = self.body.read()
        self.body.seek(0)
        return body_content
    
    def trac_messages(self, message_type):
        from BeautifulSoup import BeautifulSoup
        soup = BeautifulSoup(self.html())
        message_container = soup.find(name='div', attrs=dict(id='warning'))
        if message_container is None:
            return []
        messages_with_tags = message_container.findAll('li')
        if len(messages_with_tags) > 0:
            strip_tags = lambda html: re.sub('^<li>(.*)</li>$', r'\1', unicode(html))
            return map(strip_tags, messages_with_tags)
        pattern = '<strong>%s:</strong>\s*(.*?)\s*</div>' % message_type
        match = re.search(pattern, unicode(message_container), re.DOTALL | re.IGNORECASE)
        if match is None:
            return []
        return [match.group(1)]
    
    def trac_warnings(self):
        return self.trac_messages('Warning')


def mock_request(path, request_attributes=None, **kwargs):
    request_attributes = request_attributes or {}
    wsgi_environment = {
        'SERVER_PORT': 4711,
        'SERVER_NAME': 'foo.bar',
        
        'REMOTE_ADDR': '127.0.0.1',
        'REQUEST_METHOD': request_attributes.pop('method', 'GET'),
        'PATH_INFO': path,
        
        'wsgi.url_scheme': 'http',
        'wsgi.input': StringIO(),
    }
    wsgi_environment.update(request_attributes)
    
    response = MockResponse()
    request = Request(wsgi_environment, response.start_response)
    request.captured_response = response
    request.args = kwargs
    
    
    def populate(env):
        from trac.perm import PermissionCache
        from trac.util.datefmt import localtz
        from trac.web.session import Session
        
        self = request
        self.tz = localtz
        self.authname = 'anonymous'
        self.session = Session(env, self)
        from trac.test import MockPerm
        self.perm = PermissionCache(env, 'anonymous')
        self.form_token = None
        self.chrome = dict(warnings=[], notices=[], scripts=[])
#        self.chrome = Chrome(env).prepare_request(self),
        #{'wiki': <function <lambda> at 0x7f33f0640b90>, 'search': <function <lambda> at 0x7f33f0640c80>, 'tags': <function <lambda> at 0x7f33f0640f50>, 'chrome': <function <lambda> at 0x7f33f05611b8>, 'timeline': <function <lambda> at 0x7f33f0640de8>, 'about': <function <lambda> at 0x7f33f0640e60>, 'admin': <function <lambda> at 0x7f33f0640d70>, 'logout': <function <lambda> at 0x7f33f0640cf8>, 'prefs': <function <lambda> at 0x7f33f0640ed8>}

    
    request.populate = populate
    return request
# ------------------------------------------------------------------------------

import shutil
import tempfile

from trac import __version__ as trac_version

if trac_version.startswith('0.12'):
    from trac.test import EnvironmentStub
    EnvironmentStub = EnvironmentStub
else:
    from trac.env import Environment
    from trac.test import EnvironmentStub

    class FixedEnvironmentStub(EnvironmentStub):
        """Since the release of trac 0.11 a lot of bugs were fixed in the 
        EnvironmentStub. This class provides backports of these fixes so plugins
        can support older trac versions as well."""
        
        # See http://trac.edgewall.org/ticket/8591
        # 'Can not disable components with EnvironmentStub'
        # fixed in 0.12
        def __init__(self, default_data=False, enable=None):
            super(FixedEnvironmentStub, self).__init__(default_data=default_data, enable=enable)
            if enable is not None:
                self.config.set('components', 'trac.*', 'disabled')
            for name_or_class in enable or ():
                config_key = self.normalize_configuration_key(name_or_class)
                self.config.set('components', config_key, 'enabled')
            self._did_create_temp_directory = False
        
        def normalize_configuration_key(self, name_or_class):
            name = name_or_class
            if not isinstance(name_or_class, basestring):
                name = name_or_class.__module__ + '.' + name_or_class.__name__
            return name.lower()
        
        def is_component_enabled(self, cls):
            return Environment.is_component_enabled(self, cls)
        
        # TODO: Better naming
        def use_temp_directory(self):
            if self._did_create_temp_directory:
                return
            self.path = tempfile.mkdtemp()
            self._did_create_temp_directory = True
        
        def destroy_temp_directory(self):
            if not self._did_create_temp_directory:
                return
            shutil.rmtree(self.path)
        
        # See http://trac.edgewall.org/ticket/7619
        # 'EnvironmentStub wrong implementation of get_known_users()'
        # fixed in 0.11.2
        def get_known_users(self, db=None):
            return self.known_users
    EnvironmentStub = FixedEnvironmentStub



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
        

