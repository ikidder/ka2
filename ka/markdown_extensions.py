from markdown.inlinepatterns import InlineProcessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree

# References:
# https://python-markdown.github.io/extensions/api/
# https://github.com/Python-Markdown/markdown/blob/master/markdown/inlinepatterns.py

EXTENSION_RE = r'(?:^|[;,.?!\s])(&[^\W_]{2,30})(?=[;,.?!\s]|$)'

class ThemeInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element("a")
        el.text = m.group(1)
        el.set("href", "/theme/" + m.group(1))

        return el, m.start(1), m.end(1)

class ThemeExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(ThemeInlineProcessor(EXTENSION_RE, md), 'a', 175)