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

from pkg_resources import resource_filename

from trac.core import implements
from trac.util.datefmt import format_datetime, pretty_timedelta, to_datetime
from trac.util.translation import _
from trac.web.chrome import Chrome, add_stylesheet
from trac.wiki.formatter import wiki_to_html
from trac.wiki.macros import WikiMacroBase

from trac_wiki_blog.util import content_from_wiki_markup, \
    creation_date_of_page, get_wiki_pagename, load_pages_with_tags, \
    sort_by_creation_date, title_from_wiki_markup


__all__ = ['ShowPostsMacro']


def now():
    return to_datetime(None)


class ShowPostsMacro(WikiMacroBase):
    """Provide a list of tagged blog posts, sorted by creation time."""
    
    implements(ITemplateProvider)
    
    # WikiMacroBase
    def expand_macro(self, formatter, name, content):
        req = formatter.req
        pages = sort_by_creation_date(load_pages_with_tags(self.env, req, "blog"))
        
        # TODO: make the name of the template configurable in trac.ini
        # TODO: add creation date, modified date (if different than creation) and tags
        processed_pages = []
        for page in pages:
            processed_pages.append(self._process_page(req, page))
        
        add_stylesheet(req, 'blog/css/blog.css')
        parameters = dict(
            blog_heading = _("Blog Posts"),
            read_post_title = _("Read Post"),
            pages = processed_pages
        )
        return self._render_template(req, 'show_posts_macro.html', parameters)
    
    def _process_page(req, page):
        post_content = content_from_wiki_markup(page.text)
        creation_date = creation_date_of_page(page)
        return dict(
            title = title_from_wiki_markup(page.text),
            url = req.href.wiki(page.name),
            creation_date = format_datetime(creation_date),
            delta = pretty_timedelta(creation_date, now()),
            # TODO: Need to build custom req so relative links are correct
            content = wiki_to_html(post_content, self.env, req),
        )
    
    def _render_template(self, req, template, attributes):
        return Chrome(self.env).render_template(req, template, attributes, None)
        
    # --------------------------------------------------------------------------
    # ITemplateProvider
    def get_templates_dirs(self):
        return [resource_filename(__name__, 'templates')]
    
    def get_htdocs_dirs(self):
        return [('blog', resource_filename(__name__, 'htdocs'))]

