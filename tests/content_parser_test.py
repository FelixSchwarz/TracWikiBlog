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

import unittest

from trac_wiki_blog.util import content_from_wiki_markup, title_from_wiki_markup


class ContentParser(unittest.TestCase):
    
    # ================================================================
    # Title parsing
    
    def test_throws_error_if_no_title_is_present(self):
        self.assertRaises(ValueError, title_from_wiki_markup, "")
    
    def test_can_parse_simple_title(self):
        self.assertEquals("bla", title_from_wiki_markup("= bla ="))
    
    def test_can_parse_title_with_spaces_before_it(self):
        self.assertEquals("bla", title_from_wiki_markup(" = bla ="))
    
    def test_throws_if_title_is_missing_spaces_after_equal_signs(self):
        self.assertRaises(ValueError, title_from_wiki_markup, "=bla=")
    
    def test_can_ignore_stuff_before_first_title(self):
        self.assertEquals("bla", title_from_wiki_markup("[[Image(wiki:2007/02/09/17.55:Xaos_Screenshot.jpg, right, 400)]]\n= bla ="))
    
    def test_can_parse_shell_scripts_in_title(self):
        self.assertEquals('if [ "z$?" != "z0" ] ; then ...', title_from_wiki_markup('= if [ "z$?" != "z0" ] ; then ... = Aus dem Buildscript '))
    
    # ================================================================
    # Content parsing
    
    def test_can_extract_simple_content(self):
        self.assertEquals("bla", content_from_wiki_markup("= blub = bla"))
    
    def test_can_extract_multiline_content(self):
        self.assertEquals("bla\nblub", content_from_wiki_markup("= blub = bla\nblub"))
    
# TODO: consider changing parsing to really "extract" the title, and leave everything before and after it as the content
