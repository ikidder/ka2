import os
from ka.tests.common import ContextCase
import time
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
from ka.models import *
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
from markdown import markdown
from ka.markdown_extensions import *


class TestMarkdownExtension(ContextCase):

    def setUp(self):
        super().setUp()

        self.extensions = [ThemeExtension()]

    # list of (input, expected output, comment)
    cases = [
        ("no markdown here", "<p>no markdown here</p>", 'no markdown'),
        ('# heading ', '<h1>heading</h1>', 'h1'),
        (
            ' &theme',
            '<p><a href="/theme/&amp;theme">&amp;theme</a></p>',
            'theme by itself'),
        (
            ' &one &two',
            '<p><a href="/theme/&amp;one">&amp;one</a> <a href="/theme/&amp;two">&amp;two</a></p>',
            'two themes separated by space'
         ),
        (
            ' &one;&two',
            '<p><a href="/theme/&amp;one">&amp;one</a>;<a href="/theme/&amp;two">&amp;two</a></p>',
            'two themes separated by semicolon'
        ),
    ]

    def test_markdown_extension(self):
        for case in self.cases:
            self.assertEqual(
                case[1],
                markdown(case[0], extensions=self.extensions),
                f'input: {case[0]}, {case[2]}'
            )