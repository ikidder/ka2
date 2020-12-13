import os
from ka.tests.common import ContextCase
import time
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
from ka.models import *
from sqlalchemy.exc import IntegrityError
from ka.tests.makers import *
import re


class TestTagRegex(ContextCase):

    # list of (input, expected output, comment))
    cases = [
        ('&foo', ['&foo'], ''),
        ('&foo5', ['&foo5'], 'digits will match'),
        (' &foo', ['&foo'], 'space before'),
        ('&foo ', ['&foo'], 'space after'),
        ('\n&foo ', ['&foo'], 'new line before'),
        ('&foēÜ', ['&foēÜ'], 'non-english chars'),
        ('&fo_o', [], 'underscores will not match'),
        ('&fo-o', [], 'dashes will not match'),
        ('&fo.o', ['&fo'], 'at end of sentence will match'),
        ('&fo"o', [], 'punctuation will not match'),
        ('&fo?', ['&fo'], 'at end of sentence will match'),
        ('&-foo', [], 'punctuation will not match'),
        ('foo', [], 'missing & will not match'),
        ('&foo o', ['&foo'], 'will not span whitespace'),
        ('&foo&o ddfsj', [], 'nested tags will not match'),
        ('random &foo  &bar text', ['&foo', '&bar'], 'multiple matches in middle'),
        ('&foo random. text &bar', ['&foo', '&bar'], 'multiple matches at start and end'),
        ('&foo &bar', ['&foo', '&bar'], 'multiple separated by space'),
        ('&foo;&bar random text', ['&foo', '&bar'], 'tags separated by punctuation'),
        ('&foo, &bar random text', ['&foo', '&bar'], 'tags separated by punctuation and space'),
        ('&f', [], '1 char after the & will not match'),
        ('&foofoofoofoofoofoofoofoofoofood', [], '31 chars will not match'),
    ]

    def test_regex(self):
        for case in self.cases:
            self.assertEqual(
                case[1],
                re.findall(TAG_REGEX, case[0]),
                f'input: {case[0]}, {case[2]}')
