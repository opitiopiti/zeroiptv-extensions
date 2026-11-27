"""Offline fixtures: python -m unittest -v test_plugins (no real network)."""
import hashlib
import importlib
from pathlib import Path
import sys
import unittest
import tempfile
from unittest.mock import patch
import build
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
BASE = 'https://www.dizibox.live'
# Synthetic IDs and fixture documents (not real streams).
EP = '/sample-1-sezon-5-bolum-izle/'
KING = BASE + '/player/king/king.php?v=fixture'
KING_REQUEST = KING.replace('king.php?v=', 'king.php?wmode=opaque&v=')
EMBED = 'https://dbx.molystream.org/embed/fixture'
MANIFEST = EMBED + '/q/1'

class FakeContext:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []
    def get(self, url, **kw):
        self.calls.append((url, kw))
        data = self.pages[url]
        if isinstance(data, Exception): raise data
        return SimpleNamespace(url=url, body=data, content_type='text/html')

class PluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fields = next((line.split('\t') for line in (ROOT / 'repo.tsv').read_text().splitlines()[1:] if line.split('\t')[0] == 'dizibox'), None)
        if fields is None: raise unittest.SkipTest('DiziBox disabled or removed')
        path = ROOT / fields[7]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == fields[8]
        sys.path.insert(0, str(path))
        cls.p = importlib.import_module(f'zeroext_{fields[0]}_v{fields[1]}')

    def test_home_relative_path_and_poster(self):
        ctx = FakeContext({BASE+'/tum-bolumler/': f'''<article class="article-episode-card"><a class="episode-card-title" href="{EP}"><b class="series-name">Sample</b></a><span class="season">1. Sezon</span><b class="episode">5. Bölüm</b><img class="afis" data-src="/poster.jpg"></article><a href="/tum-bolumler/page/2/">Next</a>'''})
        result = self.p.get_home(ctx, 1)
        self.assertEqual(result['items'][0]['path'], EP)
        self.assertEqual(result['items'][0]['poster'], BASE+'/poster.jpg')
        self.assertTrue(result['next'])
    def test_series_tab(self):
        html = '<article class="article-series-poster"><a class="poster-title" href="/sample/">Sample</a></article>'
        ctx = FakeContext({BASE+f'/tur/{genre}/':html for genre in ('dram','komedi','korku')})
        mod = self.p
        self.assertEqual(len(mod.get_series(ctx,1)['items']),1)
        self.assertEqual(len(ctx.calls),3)
    def test_search(self):
        ctx = FakeContext({BASE+'/search/A+B/':'<article class="detailed-article"><h3><a href="/sample/">Sample</a></h3></article>'})
        self.assertEqual(self.p.search(ctx, 'A B')['items'][0]['title'], 'Sample')
    def test_detail_and_seasons(self):
        ctx = FakeContext({BASE+EP:f'<div class="tv-overview"><h1><a href="/sample/">Sample</a></h1></div><a class="season-episode" href="{EP}">1. Sezon 5. Bölüm</a><div id="seasons-list"><a href="/sample-season-2/">2</a></div>', BASE+'/sample-season-2/':'<a class="season-episode" href="/sample-2-sezon-1-bolum-izle/">2. Sezon 1. Bölüm</a>'})
        result = self.p.get_details(ctx, EP)
        self.assertEqual(result['path'], '/sample/')
        self.assertEqual([e['season'] for e in result['episodes']], [1,2])
        self.assertTrue(result['complete'])
        ctx.pages[BASE+'/sample-season-2/'] = OSError('fixture failure')
        self.assertFalse(self.p.get_details(ctx, EP)['complete'])
    def playback_ctx(self, body):
        return FakeContext({BASE+EP:f'<div id="video-area"><iframe src="{KING}"></iframe></div>',KING_REQUEST:f'<div id="Player"><iframe src="{EMBED}"></iframe></div>',MANIFEST:body})
    def test_hls_headers(self):
        ctx=self.playback_ctx('#EXTM3U\n#EXT-X-VERSION:3\n')
        result=self.p.resolve(ctx,EP)
        self.assertEqual(result['url'],MANIFEST)
        self.assertEqual(result['manifestHeaders']['Referer'],EMBED)
        self.assertEqual(result['headers']['Origin'],'https://dbx.molystream.org')
        self.assertEqual(result['headers']['Referer'],'https://dbx.molystream.org/')
        self.assertEqual(ctx.calls[-1][1]['headers'],result['manifestHeaders'])
        self.assertEqual(len(ctx.calls),3)
    def test_reject_html(self):
        with self.assertRaises(ValueError): self.p.resolve(self.playback_ctx('<html>not a manifest</html>'),EP)
    def test_only_dbx(self):
        ctx=FakeContext({BASE+EP:'<div id="video-area"><iframe src="https://example.com/other"></iframe></div>'})
        with self.assertRaises(ValueError): self.p.resolve(ctx,EP)
        self.assertEqual(len(ctx.calls),1)
    def test_old_domain_relative_path(self):
        common=self.p
        self.assertEqual(common.path_of('https://dizibox.live/sample/?x=1',BASE),'/sample/?x=1')
        self.assertEqual(common.path_of('https://example.com/sample/',BASE),'')

class BuildTests(unittest.TestCase):
    def test_function_driven_sections(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); folder = root/'plugins'; folder.mkdir()
            source = folder/'sample.py'
            metadata = 'ID="sample"\nNAME="Sample"\nVERSION=1\nTYPE="mixed"\nBASE_URL="https://example.com"\nPREVIOUS_HOSTS=()\nENABLED=True\n'
            mandatory = ''.join(f'def {fn}(ctx, arg): return {{}}\n' for fn in ('search','get_details','resolve'))
            movies = 'def get_movies(ctx, page=1): return {}\n'
            animes = 'def get_animes(ctx, page=1): return {}\n'
            unrelated = 'def get_popular(ctx, page=1): return {}\n'
            with patch.object(build, 'ROOT',root):
                source.write_text(metadata+mandatory+movies+animes+unrelated)
                build.build()
                self.assertEqual((root/'repo.tsv').read_text().splitlines()[1].split('\t')[6], 'filmler,animeler')
                source.write_text(metadata+mandatory+movies+unrelated)
                build.build()
                self.assertEqual((root/'repo.tsv').read_text().splitlines()[1].split('\t')[6], 'filmler')
                source.write_text(metadata+mandatory+unrelated)
                with self.assertRaises(ValueError): build.build()
    def test_build_does_not_execute_plugin(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'sample.py'
            source.write_text('ID="sample"\nNAME="Sample"\nVERSION=1\nTYPE="mixed"\nBASE_URL="https://example.com"\nPREVIOUS_HOSTS=()\nENABLED=True\nraise RuntimeError("must not execute")\n'+''.join(f'def {fn}(ctx, arg): return {{}}\n' for fn in ('search','get_details','resolve','get_movies')))
            self.assertEqual(build.inspect_source(source)[1], ['filmler'])
    def test_deterministic_packages(self):
        before=(ROOT/'repo.tsv').read_bytes()
        build.build()
        self.assertEqual((ROOT/'repo.tsv').read_bytes(),before)

if __name__=='__main__': unittest.main()
