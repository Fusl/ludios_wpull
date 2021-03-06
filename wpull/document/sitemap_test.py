import codecs
import gzip
import io
import unittest

from wpull.document.base_test import CODEC_NAMES, EBCDIC
from wpull.document.htmlparse.lxml_ import HTMLParser
from wpull.document.sitemap import SitemapReader
from wpull.protocol.http.request import Request
from wpull.url import URLInfo


class TestSitemap(unittest.TestCase):
    def test_sitemap_encoding(self):
        parser = HTMLParser()
        reader = SitemapReader(parser)

        bom_map = {
            'utf_16_le': codecs.BOM_UTF16_LE,
            'utf_16_be': codecs.BOM_UTF16_BE,
            'utf_32_le': codecs.BOM_UTF32_LE,
            'utf_32_be': codecs.BOM_UTF32_BE,
        }

        for name in CODEC_NAMES:
            if name in EBCDIC or name == 'utf_8_sig':
                # XXX: we're assuming that all codecs are ASCII backward
                # compatable
                continue

            if name.startswith('utf_16') or name.startswith('utf_32'):
                # FIXME: libxml/lxml doesn't like it when we pass in a codec
                # name but don't specify the endian but BOM is included
                continue

            data = io.BytesIO(
                bom_map.get(name, b'') +
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<urlset><url><loc>blah</loc></url></urlset>'.encode(name)
            )

            print('->', name)

            links = tuple(reader.iter_links(data, encoding=name))
            link = links[0]
            self.assertEqual('blah', link)

    def test_sitemap_detect(self):
        # It should detect without BOM
        self.assertTrue(SitemapReader.is_file(
            io.BytesIO('<?xml > <urlset >'.encode('utf-16le'))
        ))
        self.assertFalse(SitemapReader.is_file(
            io.BytesIO('<!DOCTYPE html><html><body>'.encode('utf-16le'))
        ))
        self.assertFalse(SitemapReader.is_file(
            io.BytesIO(b'<html><body>hello<urlset>')
        ))
        self.assertTrue(SitemapReader.is_file(
            io.BytesIO(b'<?xml version> <urlset>')
        ))

        data_file = io.BytesIO()
        g_file = gzip.GzipFile(fileobj=data_file, mode='wb')
        g_file.write('<?xml version> <urlset>'.encode('utf-16le'))
        g_file.close()
        data_file.seek(0)
        self.assertTrue(SitemapReader.is_file(
            data_file
        ))

        self.assertTrue(
            SitemapReader.is_url(URLInfo.parse('example.com/sitemaps1.xml'))
        )
        self.assertTrue(
            SitemapReader.is_url(URLInfo.parse('example.com/robots.txt'))
        )
        self.assertFalse(
            SitemapReader.is_url(URLInfo.parse('example.com/image.jpg'))
        )
        self.assertTrue(
            SitemapReader.is_request(Request('example.com/sitemaps34.xml'))
        )
        self.assertFalse(
            SitemapReader.is_request(Request('example.com/image.jpg'))
        )
