from markdown.inlinepatterns import InlineProcessor, LinkInlineProcessor, LINK_RE, AutolinkInlineProcessor, AUTOLINK_RE
from markdown.extensions import Extension
import xml.etree.ElementTree as etree
from urllib.parse import quote

# References:
# https://python-markdown.github.io/extensions/api/
# https://github.com/Python-Markdown/markdown/blob/master/markdown/inlinepatterns.py

# Note: May want to sanitize text with something like https://bleach.readthedocs.io/en/latest/clean.html
# The EscapeHtmlExtension is believed to be sufficient for now.

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


class NoImagesExtension(Extension):
    def extendMarkdown(self, md):
        del md.inlinePatterns['image_link']
        del md.inlinePatterns['image_reference']


class EscapeHtmlExtension(Extension):
    def extendMarkdown(self, md):
        del md.preprocessors['html_block']
        del md.inlinePatterns['html']


class ModifiedLinkInlineProcessor(LinkInlineProcessor):
    """Open link (safely!) in new tab.
    reference: https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html#tabnabbing
    """
    def handleMatch(self, m, data):
        el, start, end = super().handleMatch(m, data)
        if el is not None:
            el.set('target', '_blank')
            el.set('rel', 'noopener noreferrer')
        return el, start, end


class ModifiedLinkExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(ModifiedLinkInlineProcessor(LINK_RE, md), 'link', 160)


class ModifiedAutoLinkInlineProcessor(AutolinkInlineProcessor):
    """Open link (safely!) in new tab.
    reference: https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html#tabnabbing
    """
    def handleMatch(self, m, data):
        el, start, end = super().handleMatch(m, data)
        if el is not None:
            el.set('target', '_blank')
            el.set('rel', 'noopener noreferrer')
        return el, start, end


class ModifiedAutoLinkExtension(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(ModifiedAutoLinkInlineProcessor(AUTOLINK_RE, md), 'autolink', 120)








