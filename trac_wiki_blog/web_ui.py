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

from genshi.builder import tag
from pkg_resources import resource_filename
from trac.core import implements
from trac.util.translation import _
from trac.web import IRequestHandler
from trac.web.chrome import INavigationContributor, ITemplateProvider
from trac.wiki.web_ui import WikiModule
from tractags.api import TagSystem
from tractags.wiki import WikiTagInterface

from trac_wiki_blog.util import get_wiki_pagename



__all__ = ['NewPostModule', 'NewPostTagInterface']


_tag_split = re.compile('[,\s]+')


class NewPostModule(WikiModule):
    """Provides a convenient form to enter a new blog-post."""
    
    implements(INavigationContributor)
    
    # TODO: add precautions so two posts at the day with the same name don't overwrite
    # TODO: add more escapes to the wiki page name
    # TODO: limit blog post user friendly name length
    
    # Implementation IRequestHandler
    def match_request(self, req):
        return req.path_info == '/newblogpost'
    
    # -----------------------------------------------------------------------
    # TODO: Needs good tests!
    # copied from tracblog
    def _get_tags(self, req):
        """ Return a list of tags.
        
        First look for the presence of the `tags` query argument. If found,
        parse the result into a list.
        
        Otherwise, look for the `tag` query arguments.
        
        If none of the previous query arguments exist, use the list of tags
        from `trac.ini`
        
        """
        taglist = req.args.get('tags', None)
        if taglist:
            tags = [t.strip() for t in _tag_split.split(taglist) if t.strip()]
        elif req.args.has_key('tag'):
            tags = req.args.getlist('tag')
        else:
            tags = ['blog']
        return tags
    # -----------------------------------------------------------------------
    
    
    def _do_save(self, req, versioned_page):
        title = req.args.get('blogtitle')
        content = '= %s =\n\n%s' % (title, req.args.get('text', ''))
        req.args['text'] = content
        tags = ['blog'] + self._get_tags(req)
        tag_system = TagSystem(self.env)
        tag_system.add_tags(req, versioned_page.resource, tags)
        result = super(NewPostModule, self)._do_save(req, versioned_page)
        return result
    
    def _render_editor(self, req, page, action='edit', has_collision=False):
        result = super(NewPostModule, self)._render_editor(req, 
                       page, action=action, has_collision=has_collision)
        template, data, content_type = result
        data['blog'] = dict(title=req.args.get('blogtitle'))
        return 'newblogpost.html', data, content_type
    
    def process_request(self, req):
        if req.method == 'POST':
            title = req.args.get('blogtitle', '').strip()
            if title == '':
                add_warning(req, _("You need to provide a post title!"))
                req.args['preview'] = True
                wiki_page = '' # only rendered in window title
            else:
                wiki_page = get_wiki_pagename(datetime.date.today(), title)
            req.args['page'] = wiki_page
        else:
            req.args['page'] = '_new_blog_template'
        req.args['action'] = 'edit'
        return super(NewPostModule, self).process_request(req)
    
    # ITemplateProvider
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]
    
    def get_htdocs_dirs(self):
        return [('blog', resource_filename(__name__, 'htdocs'))]
    
    # ITimelineEventProvider methods
    def get_timeline_filters(self, req):
        # We inherit from WikiModule to re-use many of the page-saving code.
        # However we inherit the ITimelineEventProvider implementation. If we
        # leave it untouched, all Wiki edits will be doubled in the timeline.
        return []
    
    def get_timeline_events(self, req, start, stop, filters):
        return []
    
    # IPermissionRequestor methods
    def get_permission_actions(self):
        return []
    
    # INavigationContributor
    def get_active_navigation_item(self, req):
        return 'blog'
    
    def get_navigation_items(self, req):
        if ('WIKI_CREATE' not in req.perm) or ('TAGS_MODIFY' not in req.perm):
            return
        yield ('mainnav', 'blog', tag.a(_('New Blog Post'), href=req.href.newblogpost()))



class NewPostTagInterface(WikiTagInterface):
    """Adds trac tags for the new blog post page."""
    
    def _may_edit_tags(self, req, data):
        page = data.get("page")
        if page != None:
            return 'TAGS_MODIFY' in req.perm(page.resource)
        return False
    
    # ITemplateStreamFilter methods
    def filter_stream(self, req, method, filename, stream, data):
        if filename == 'newblogpost.html' and self._may_edit_tags(req, data):
            return self._wiki_edit(req, stream)
        return stream

