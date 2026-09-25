"""Behavior regressions for the product-description triage fixes.

Run with Python Playwright and its installed Chromium headless shell:
  python3 tests/browser_regressions.py

Resources are fulfilled from the checkout at a test origin. Clean URLs such as
/work/everag resolve to work/everag.html, as on Cloudflare Pages. No preview server,
external service, installed Chrome profile, or system-clock change is needed.
Set PLAYWRIGHT_CHROMIUM_EXECUTABLE to use another bundled Chromium binary.
"""
import json
import mimetypes
import os
import re
from pathlib import Path
import time
import unittest
from urllib.parse import unquote, urljoin, urlsplit
from xml.etree import ElementTree

from playwright.sync_api import sync_playwright

ROOT = Path(os.environ.get('SPIDLEWEB_TEST_ROOT', Path(__file__).resolve().parents[1]))
ORIGIN = 'https://portfolio.test'
CASE_PAGES = [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'work').glob('*.html')) if p.name != 'index.html']
# The Work and Writing indexes and the posts (Phase 2C).
READING_PAGES = ['work/index.html', 'writing/index.html',
                 *[str(p.relative_to(ROOT)) for p in sorted((ROOT / 'writing').glob('*.html')) if p.name != 'index.html']]
PAGES = ['index.html', 'list/index.html', *CASE_PAGES, *READING_PAGES, '404.html']
# /work/ lists the case studies newest first, and the next-story band follows it.
WORK_ORDER = ['expert-insights', 'campaign-sim', 'everag', 'vidscrip', 'conservis', 'plinth']
SCREENSHOTS = os.environ.get('SPIDLEWEB_TEST_SCREENSHOTS')


class BrowserRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        candidates = sorted(Path.home().glob(
            'Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell'))
        executable = os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE')
        if not executable and candidates:
            executable = str(candidates[-1])
        cls.browser = cls.playwright.chromium.launch(executable_path=executable)
        print(f'Browser: Chromium {cls.browser.version}', flush=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.contexts = []

    def tearDown(self):
        for context in self.contexts:
            context.close()

    def context(self, block_script=False, **options):
        options.setdefault('viewport', {'width': 1440, 'height': 900})
        context = self.browser.new_context(**options)
        context.scripts_enabled = options.get('java_script_enabled', True)
        context.set_default_timeout(5000)
        self.contexts.append(context)

        def route_resource(route):
            url = urlsplit(route.request.url)
            if url.netloc != 'portfolio.test':
                if route.request.is_navigation_request():
                    route.fulfill(content_type='text/html', body='<title>External destination fixture</title>Destination')
                else:
                    route.abort()
                return
            if block_script and url.path == '/script.js':
                route.abort()
                return
            path = (ROOT / unquote(url.path).lstrip('/')).resolve()
            if path.is_relative_to(ROOT) and path.is_dir():
                path = path / 'index.html'
            elif not path.exists() and not url.path.endswith('/'):
                # Pages serves a clean URL such as /work/everag from work/everag.html.
                path = path.with_name(f'{path.name}.html')
            if not path.is_relative_to(ROOT) or not path.is_file():
                route.fulfill(status=404, body='Not found')
                return
            content_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
            route.fulfill(content_type=content_type, body=path.read_bytes())

        context.route('**/*', route_resource)
        return context

    def open(self, context, path='index.html'):
        page = context.new_page()
        page.errors = []
        page.on('pageerror', lambda error: page.errors.append(str(error)))
        page.goto(f'{ORIGIN}/{path}')
        page.evaluate('document.fonts.ready')
        self.settle(page)
        return page

    def settle(self, page):
        if not page.context.scripts_enabled:
            return
        page.evaluate('() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))')

    def assert_visible(self, page, motionless=False):
        check = '''motionless => [...document.querySelectorAll('.reveal')].every(el => {
          const style = getComputedStyle(el);
          return style.opacity === '1' && style.transform === 'none' &&
            (!motionless || style.transitionDuration.split(',').every(value => parseFloat(value) === 0));
        })'''
        if page.context.scripts_enabled:
            page.wait_for_function(check, arg=motionless)
        else:
            self.assertTrue(page.evaluate(check, motionless))

    def scroll_reveals(self, page):
        for target in page.locator('.reveal').all():
            target.evaluate('el => el.scrollIntoView()')
            page.wait_for_function('el => getComputedStyle(el).opacity === "1"', arg=target.element_handle())
        self.assert_visible(page)

    def screenshot(self, page, name):
        if SCREENSHOTS:
            directory = Path(SCREENSHOTS)
            directory.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(directory / f'{name}.png'))

    def test_b01_blocked_script_and_no_javascript_keep_all_pages_readable(self):
        for options in ({'block_script': True}, {'block_script': True, 'reduced_motion': 'reduce'},
                        {'java_script_enabled': False}):
            context = self.context(**options)
            for path in PAGES:
                with self.subTest(path=path, options=options):
                    page = self.open(context, path)
                    self.assert_visible(page, motionless=True)
                    self.assertTrue(page.locator('h1').is_visible())
                    self.assertEqual(page.errors, [])
                    if path == 'index.html' and options == {'block_script': True}:
                        self.screenshot(page, 'b01-blocked-script')
                    page.close()

    def test_b02_fresh_malformed_unknown_and_encoded_fragments(self):
        # Replaces the old section-nav version: a fragment on the homepage now
        # names a card, and a malformed or unknown one is ignored quietly.
        context = self.context()
        for fragment in ['#%', '#[', '#missing-section', '#%72etirement-education-library']:
            with self.subTest(fragment=fragment):
                page = self.open(context, f'index.html{fragment}')
                self.assertEqual(page.errors, [])
                cards = page.locator('.stream-card').evaluate_all('els => els.map(el => el.id)')
                shown = page.locator('.stream-card:not([hidden])').count()
                if fragment.startswith('#%72'):
                    self.assertTrue(page.locator('#retirement-education-library').is_visible())
                    self.assertEqual(shown, max(30, cards.index('retirement-education-library') + 1))
                else:
                    self.assertEqual(shown, min(30, len(cards)))
                page.close()
        context = self.context()
        context.add_init_script('delete window.IntersectionObserver')
        page = self.open(context, 'index.html#%')
        self.assertEqual(page.locator('.view-dock').count(), 0)
        self.assertEqual(page.locator('.stream-card:not([hidden])').count(), 30)
        self.assertEqual(page.errors, [])

    def test_b03_initial_and_live_reduced_motion(self):
        context = self.context(reduced_motion='reduce')
        for path in PAGES:
            page = self.open(context, path)
            self.assert_visible(page, motionless=True)
            page.close()
        # The homepage's one motion is the docked bar's slide, which reduced
        # motion drops live, without a reload.
        page = self.open(self.context(reduced_motion='no-preference'), 'index.html')
        duration = "document.querySelector('.view-dock') && getComputedStyle(document.querySelector('.view-dock')).transitionDuration"
        self.assertNotEqual(page.evaluate(duration), '0s')
        page.emulate_media(reduced_motion='reduce')
        self.assertEqual(page.evaluate(duration), '0s')
        page.emulate_media(reduced_motion='no-preference')
        self.assertNotEqual(page.evaluate(duration), '0s')
        self.assertEqual(page.errors, [])

    def test_b06_flowing_case_context_on_short_screens(self):
        for width in [1440, 800]:
            context = self.context(viewport={'width': width, 'height': 400})
            for path in CASE_PAGES:
                page = self.open(context, path)
                rail = page.locator('.case-context')
                self.assertEqual(rail.evaluate('el => getComputedStyle(el).position'), 'static')
                rail.locator('p').last.scroll_into_view_if_needed()
                self.assertTrue(rail.locator('p').last.is_visible())
                self.assertEqual(rail.evaluate('el => el.scrollHeight'), rail.evaluate('el => el.clientHeight'))
                page.close()

    def test_b07_mobile_masthead_name_returns_home_on_every_case(self):
        # The site masthead replaces the case masthead's Index link: on a phone
        # the name leads home, and the menu trigger names Work.
        context = self.context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        for path in CASE_PAGES:
            with self.subTest(path=path):
                page = self.open(context, path)
                self.assertEqual(page.locator('.masthead__trigger').text_content(), 'Menu, Work')
                link = page.locator('.masthead__name a')
                self.assertTrue(link.is_visible())
                bounds = link.bounding_box()
                self.assertGreaterEqual(bounds['y'], 0)
                self.assertLess(bounds['y'] + bounds['height'], 844)
                if path == 'work/expert-insights.html':
                    self.screenshot(page, 'b07-mobile-index')
                link.tap()
                page.wait_for_url(f'{ORIGIN}/')
                self.assertIn('JASON', page.locator('h1').inner_text())
                page.close()

    def test_b09_every_footer_uses_the_same_current_year_and_fallback(self):
        context = self.context()
        context.add_init_script('''{
          const OriginalDate = Date;
          window.Date = class extends OriginalDate {
            constructor(...args) { super(...(args.length ? args : ['2027-06-15T12:00:00Z'])); }
            static now() { return new OriginalDate('2027-06-15T12:00:00Z').getTime(); }
          };
        }''')
        for path in PAGES:
            page = self.open(context, path)
            self.assertIn('© 2027 JASON SPIDLE', page.locator('.footer, .footline').first.inner_text())
            page.close()
        context = self.context(java_script_enabled=False)
        for path in PAGES:
            page = self.open(context, path)
            self.assertIn('© 2026 JASON SPIDLE', page.locator('.footer, .footline').first.inner_text())
            page.close()

    def test_b10_external_links_use_this_tab_and_preserve_back_navigation(self):
        context = self.context(reduced_motion='reduce')
        count = 0
        for path in PAGES:
            page = self.open(context, path)
            links = page.locator('a[href^="https://"]').evaluate_all('''els => [...new Map(els
              .filter(el => el.getClientRects().length)
              .map(el => [el.getAttribute("href"), {href: el.getAttribute("href"), url: el.href}])).values()]''')
            for link_info in links:
                href = link_info['href']
                with self.subTest(path=path, href=href):
                    link = page.locator(f'a[href="{href}"]:not(.about a)').first
                    self.assertIn(link.get_attribute('target'), [None, '_self'])
                    link.click()
                    page.wait_for_url(link_info['url'])
                    self.assertEqual(len(context.pages), 1)
                    self.assertEqual(page.title(), 'External destination fixture')
                    page.go_back()
                    page.wait_for_url(f'{ORIGIN}/{path}')
                    count += 1
            page.close()
        # Craft in Grid dropped the old homepage's Featured and Sites links, six
        # of the links this counted, so the floor moved from 15 to 12.
        self.assertGreaterEqual(count, 12)
        page = self.open(context)
        with context.expect_page() as opened:
            page.locator('.footline a[href^="https://"]').click(modifiers=['ControlOrMeta'])
        destination = opened.value
        destination.wait_for_load_state()
        self.assertEqual(destination.title(), 'External destination fixture')
        self.assertEqual(page.url, f'{ORIGIN}/index.html')
        destination.close()

    def test_all_pages_fit_desktop_and_mobile_and_finish_revealing(self):
        for width, height in [(1440, 900), (390, 844), (320, 844)]:
            context = self.context(viewport={'width': width, 'height': height})
            for path in PAGES:
                with self.subTest(viewport=(width, height), path=path):
                    page = self.open(context, path)
                    self.scroll_reveals(page)
                    self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                    self.assertEqual(page.errors, [])
                    page.close()

    # ---- Craft in Grid and the site chrome (Phase 2A) ----

    def craft_cards(self, page):
        return page.locator('.stream-card').evaluate_all("""els => els.map(el => ({id: el.id,
          type: el.dataset.type, industry: el.dataset.industry}))""")

    def test_craft_is_complete_and_readable_without_its_script(self):
        # With JavaScript off, or with site.js failing to load, every card shows
        # as a real link, the places stay a row of links, and nothing dead shows.
        for label, options in [('no javascript', {'java_script_enabled': False}), ('site.js blocked', {})]:
            for width in [1440, 390]:
                with self.subTest(label, width=width):
                    context = self.context(viewport={'width': width, 'height': 900}, **options)
                    if label == 'site.js blocked':
                        context.route('**/site.js', lambda route: route.abort())
                    page = self.open(context)
                    self.assertFalse(page.evaluate("document.documentElement.classList.contains('js')"))
                    total = page.locator('.stream-card').count()
                    self.assertGreaterEqual(total, 30)
                    self.assertEqual(page.locator('.stream-card__link:visible').count(), total)
                    for selector in ['[data-filters]', '[data-pager]', '.masthead__trigger', '.view-dock', '#about']:
                        self.assertEqual(page.locator(f'{selector}:visible').count(), 0, selector)
                    self.assertEqual(page.locator('.masthead__places a:visible').count(), 4)
                    self.assertEqual(page.locator('.legend__item:visible').count(), 3)
                    self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                    # About opens through :target, and Close takes it away again.
                    page.locator('.masthead__places a[href="#about"]').click()
                    self.assertTrue(page.locator('#about').is_visible())
                    self.assertTrue(page.locator('.about .email').get_attribute('href').startswith('mailto:'))
                    page.locator('.about__close').click()
                    self.assertFalse(page.locator('#about').is_visible())
                    self.assertEqual(page.errors, [])
                    context.close()

    def test_craft_cards_keep_the_contract_links_and_outline(self):
        page = self.open(self.context(java_script_enabled=False))
        self.assertEqual(page.locator('h1').count(), 1)
        self.assertEqual(page.locator('.masthead__name').evaluate('el => el.tagName'), 'H1')
        cards = page.locator('.stream-card').evaluate_all("""els => els.map(el => {
          const links = el.querySelectorAll('a');
          const link = links[0];
          return {id: el.id, type: el.dataset.type, count: links.length, href: link.getAttribute('href'),
            open: link.dataset.open, title: el.querySelector('h2.stream-card__title') !== null,
            caseStudy: el.dataset.caseStudy || null, industry: el.dataset.industry};
        })""")
        self.assertEqual(len({card['id'] for card in cards}), len(cards))
        for card in cards:
            with self.subTest(card=card['id']):
                self.assertEqual(card['count'], 1)
                self.assertEqual(card['open'], card['id'])
                self.assertTrue(card['title'])
                self.assertTrue(card['industry'])
                href = card['href']
                if card['type'] == 'case-study':
                    self.assertEqual(href, f"/work/{card['caseStudy']}")
                elif href.startswith('/work/'):
                    self.assertRegex(href, rf"^/work/{card['caseStudy']}#fig-[a-z0-9-]+$")
                elif href.startswith('/writing/'):
                    self.assertEqual(card['type'], 'post')
                else:
                    self.assertEqual(href, f"/#{card['id']}")
        # The first row loads eagerly, and every image the cards use decodes.
        self.assertEqual(page.locator('.stream-card img[loading="eager"]').count(),
                         page.locator('.stream-card:nth-child(-n+5) img').count())
        page.close()
        page = self.open(self.context(reduced_motion='reduce'))
        self.assertTrue(page.locator('.stream-card img').evaluate_all("""async images => {
          images.forEach(image => { image.loading = 'eager'; });
          await Promise.all(images.map(image => image.decode()));
          return images.every(image => image.naturalWidth > 0);
        }"""))

    def test_craft_pagination_and_filters_agree(self):
        page = self.open(self.context(reduced_motion='reduce'))
        cards = self.craft_cards(page)
        total = len(cards)
        shown = min(30, total)
        pager = page.locator('[data-pager]')
        self.assertEqual(page.locator('.stream-card:not([hidden])').count(), shown)
        self.assertEqual(pager.locator('.pager__count').text_content(), f'{shown} of {total} items')
        self.assertEqual(pager.locator('.pager__more').text_content().split('↓')[0].strip(),
                         f'Show {min(30, total - shown)} more')
        # Right-aligned under the last column
        last = page.locator('.stream-card').nth(4).bounding_box()
        box = pager.bounding_box()
        self.assertAlmostEqual(box['x'], last['x'], delta=1)
        self.assertAlmostEqual(box['width'], last['width'], delta=1)
        first_new = cards[shown]['id']
        page.locator('.pager__more').click()
        self.assertEqual(page.locator('.stream-card:not([hidden])').count(), min(60, total))
        self.assertEqual(page.evaluate('document.activeElement.closest("article")?.id'), first_new)
        if total <= 60:
            self.assertTrue(page.locator('.pager__more').is_hidden())
        # Coming back keeps what was shown.
        page.reload()
        self.settle(page)
        self.assertEqual(page.locator('.stream-card:not([hidden])').count(), min(60, total))

        page = self.open(self.context(reduced_motion='reduce'))
        page.evaluate("document.addEventListener('stream:layout', () => { window.layouts = (window.layouts || 0) + 1; })")
        prototypes = [card for card in cards if card['type'] == 'prototype']
        page.locator('select[data-filter="type"]').select_option('prototype')
        # An open panel re-anchors when the filtered rows move (stream.js).
        self.assertGreaterEqual(page.evaluate('window.layouts'), 1)
        self.assertEqual(page.locator('.stream-card:not([hidden])').count(), min(30, len(prototypes)))
        self.assertEqual(page.locator('.pager__count').text_content(), f'{len(prototypes)} of {len(prototypes)} items')
        self.assertTrue(page.url.endswith('?type=prototype'))
        self.assertEqual(page.locator('[data-filter-label="type"]').text_content(), 'Prototypes')
        self.assertTrue(page.locator('.stream-card:not([hidden])').evaluate_all(
            "els => els.every(el => el.dataset.type === 'prototype')"))
        # Industry counts follow the type already chosen, and empty ones are off.
        options = page.locator('select[data-filter="industry"] option').evaluate_all(
            "els => els.map(el => [el.value, el.textContent, el.disabled])")
        for value, text, disabled in options[1:]:
            count = sum(card['industry'] == value for card in prototypes)
            self.assertTrue(text.endswith(f'({count})'), text)
            self.assertEqual(disabled, count == 0)
        industry = prototypes[0]['industry']
        page.locator('select[data-filter="industry"]').select_option(industry)
        both = [card for card in prototypes if card['industry'] == industry]
        self.assertEqual(page.locator('.stream-card:not([hidden])').count(), len(both))
        self.assertIn(f'industry={industry}', page.url)

        # No match shows a way out, and unknown values are ignored.
        page.goto(f'{ORIGIN}/index.html?type=reel&industry=finance')
        self.settle(page)
        self.assertEqual(page.locator('.stream-card:not([hidden])').count(), 0)
        self.assertTrue(page.locator('[data-stream-empty]').is_visible())
        self.assertTrue(page.locator('[data-pager]').is_hidden())
        page.locator('[data-filters-clear]').click()
        self.assertEqual(page.locator('.stream-card:not([hidden])').count(), shown)
        self.assertEqual(urlsplit(page.url).query, '')
        page.goto(f'{ORIGIN}/index.html?type=nonsense')
        self.settle(page)
        self.assertEqual(page.locator('.stream-card:not([hidden])').count(), shown)
        self.assertEqual(page.errors, [])

    def test_craft_deep_links_reveal_everything_up_to_their_card(self):
        context = self.context(reduced_motion='reduce')
        page = self.open(context)
        ids = [card['id'] for card in self.craft_cards(page)]
        last = ids[-1]
        page.close()
        page = self.open(context, f'index.html#{last}')
        self.assertTrue(page.locator(f'#{last}').is_visible())
        self.assertEqual(page.locator('.stream-card:not([hidden])').count(), len(ids))
        box = page.locator(f'#{last}').bounding_box()
        self.assertLess(box['y'], 900)
        self.assertGreaterEqual(box['y'] + box['height'], 0)
        page.close()
        # stream.js asks for a card with stream:reveal. A filter that hides it
        # is cleared, since the card was asked for by name.
        page = self.open(context)
        page.locator('select[data-filter="type"]').select_option('tool')
        page.evaluate("id => document.dispatchEvent(new CustomEvent('stream:reveal', {detail: {id}}))", last)
        self.assertTrue(page.locator(f'#{last}').is_visible())
        self.assertEqual(page.locator('select[data-filter="type"]').input_value(), '')
        # A same-page link to a hidden card reveals it and scrolls to it.
        page = self.open(context)
        page.evaluate('id => { location.hash = id; }', last)
        page.wait_for_function('id => !document.getElementById(id).hidden', arg=last)
        self.settle(page)
        self.assertLess(page.locator(f'#{last}').bounding_box()['y'], 900)
        self.assertEqual(page.errors, [])

    def test_masthead_matches_the_board_and_keeps_targets(self):
        page = self.open(self.context(reduced_motion='reduce'))
        name = page.locator('.masthead__name a').bounding_box()
        switch = page.locator('.view-switch').bounding_box()
        places = page.locator('.masthead__places').bounding_box()
        self.assertAlmostEqual(name['x'], 40, delta=1)
        self.assertAlmostEqual(switch['x'] + switch['width'] / 2, 720, delta=1)
        self.assertAlmostEqual(switch['y'], 34.5, delta=1)
        self.assertAlmostEqual(switch['height'], 35, delta=1)
        self.assertAlmostEqual(places['x'] + places['width'], 1400, delta=2)
        self.assertEqual(page.locator('.masthead__places a[aria-current="page"]').text_content(), 'Craft')
        self.assertEqual(page.locator('.view-switch a[aria-current="page"]').get_attribute('href'), '/')
        for link in page.locator('.masthead__places a, .masthead__name a').all():
            self.assertGreaterEqual(link.bounding_box()['height'], 44)
        # The switcher's 35px segments reach 44px through their hit areas.
        for link in page.locator('.view-switch a').all():
            box = link.bounding_box()
            hit = page.evaluate('([x, y]) => document.elementFromPoint(x, y).closest("a")?.getAttribute("href")',
                                [box['x'] + box['width'] / 2, box['y'] - 4])
            self.assertEqual(hit, link.get_attribute('href'))
        page.close()
        page = self.open(self.context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True))
        trigger = page.locator('.masthead__trigger')
        self.assertTrue(trigger.is_visible())
        self.assertGreaterEqual(trigger.bounding_box()['height'], 44)
        self.assertEqual(trigger.text_content(), 'Menu, Craft')
        switch = page.locator('.view-switch').bounding_box()
        self.assertEqual((switch['x'], switch['width']), (16, 358))
        for link in page.locator('.view-switch a').all():
            self.assertGreaterEqual(link.bounding_box()['height'], 44)

    def test_phone_menu_is_a_disclosure_that_closes_four_ways(self):
        page = self.open(self.context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True,
                                      reduced_motion='reduce'))
        trigger = page.locator('.masthead__trigger')
        places = page.locator('#site-places')
        self.assertEqual(trigger.get_attribute('aria-controls'), 'site-places')
        self.assertEqual(trigger.get_attribute('aria-expanded'), 'false')
        self.assertTrue(places.is_hidden())
        switch_y = page.locator('.view-switch').bounding_box()['y']

        def open_menu():
            trigger.tap()
            self.assertEqual(trigger.get_attribute('aria-expanded'), 'true')
            self.assertTrue(places.is_visible())

        open_menu()
        rows = places.locator('a')
        self.assertEqual(rows.count(), 4)
        for row in rows.all():
            self.assertGreaterEqual(row.bounding_box()['height'], 48)
        # It opens in place, pushing the switcher down.
        self.assertGreater(page.locator('.view-switch').bounding_box()['y'], switch_y + 4 * 48)
        self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), 390)
        trigger.tap()
        self.assertEqual(trigger.get_attribute('aria-expanded'), 'false')
        open_menu()
        page.keyboard.press('Escape')
        self.assertTrue(places.is_hidden())
        self.assertEqual(page.evaluate('document.activeElement.className'), trigger.get_attribute('class'))
        open_menu()
        page.locator('.craft-head__line').tap()
        self.assertTrue(places.is_hidden())
        open_menu()
        # A picked row closes the menu and leaves focus to where it leads.
        places.locator('a[href="#about"]').tap()
        self.assertTrue(places.is_hidden())
        self.assertTrue(page.locator('#about').is_visible())
        self.assertEqual(page.errors, [])

    def test_email_copies_with_desktop_and_touch_states(self):
        for width in [1440, 390]:
            touch = width < 600
            context = self.context(viewport={'width': width, 'height': 844}, is_mobile=touch, has_touch=touch,
                                   permissions=['clipboard-read', 'clipboard-write'])
            page = self.open(context)
            email = page.locator('.footline .email')
            self.assertEqual(email.get_attribute('href'), 'mailto:jason@spidleweb.net')
            email.scroll_into_view_if_needed()
            glyph = email.locator('.email__glyph')
            self.assertEqual(glyph.is_visible(), touch)
            email.tap() if touch else email.click()
            page.wait_for_function('el => el.hasAttribute("data-copied")', arg=email.element_handle())
            self.assertEqual(page.evaluate('navigator.clipboard.readText()'), 'jason@spidleweb.net')
            # The live region fills on the next frame, so a repeat copy is announced again.
            page.wait_for_function("document.querySelector('[role=status]')?.textContent === 'Copied to clipboard'")
            if touch:
                self.assertEqual(email.locator('.email__done').text_content(), 'Copied to clipboard ✓')
                self.assertTrue(email.locator('.email__done').is_visible())
                self.assertTrue(email.locator('.email__address').is_hidden())
            else:
                tip = email.locator('.email__tip')
                self.assertEqual(tip.text_content(), 'Copied to clipboard')
                self.assertEqual(tip.evaluate('el => getComputedStyle(el).opacity'), '1')
            self.assertEqual(urlsplit(page.url).path, '/index.html')
            page.wait_for_function('el => !el.hasAttribute("data-copied")', arg=email.element_handle(), timeout=3000)
            self.assertEqual(page.errors, [])
            context.close()

    def test_docked_bar_follows_scroll_and_steps_aside_for_the_legend(self):
        for width, height in [(1440, 900), (390, 844)]:
            page = self.open(self.context(viewport={'width': width, 'height': height}, reduced_motion='reduce'))
            dock = page.locator('.view-dock')
            hidden = 'el => el.hasAttribute("data-hidden")'
            self.assertTrue(dock.evaluate(hidden))
            self.assertEqual(dock.locator('a').evaluate_all('els => els.map(el => [el.getAttribute("href"), el.getAttribute("aria-current")])'),
                             [['/', 'page'], ['/list/', None]])
            page.mouse.move(width / 2, height / 2)
            page.mouse.wheel(0, 1200)
            page.wait_for_function('() => scrollY > 1000')
            self.settle(page)
            self.assertTrue(dock.evaluate(hidden))
            page.mouse.wheel(0, -200)
            page.wait_for_function('el => !el.hasAttribute("data-hidden")', arg=dock.element_handle())
            box = dock.bounding_box()
            self.assertGreater(box['y'] + box['height'], height - 40)
            self.assertLess(box['y'] + box['height'], height)
            if width < 600:
                self.assertEqual((box['x'], box['width']), (16, 358))
            else:
                self.assertAlmostEqual(box['x'] + box['width'] / 2, width / 2, delta=1)
            page.evaluate('scrollTo(0, document.documentElement.scrollHeight)')
            page.wait_for_function('el => el.hasAttribute("data-hidden")', arg=dock.element_handle())
            self.assertFalse(dock.is_visible())
            self.assertEqual(page.errors, [])
            page.close()

    # ---- Craft in List (Phase 2D) ----

    def list_rows(self, page):
        return page.locator('.stream-row').evaluate_all("""els => els.map(el => ({id: el.id,
          type: el.dataset.type, industry: el.dataset.industry}))""")

    def page_part(self, path, pattern):
        """One block of a page's source, found by a regular expression."""
        match = re.search(pattern, (ROOT / path).read_text(), re.S)
        self.assertIsNotNone(match, f'{pattern} in {path}')
        return match.group(0)

    def test_list_carries_the_craft_chrome_with_list_current(self):
        # The same masthead, About, head, filters, pagination, and footer line
        # as the Grid, word for word, and the same styles and scripts.
        for pattern in [r'<header class="masthead".*?</header>', r'<section class="about".*?</section>',
                        r'<div class="craft-head">.*?\n    </div>\n', r'<div class="stream-foot">.*?</main>',
                        r'<div class="footline micro">.*?</footer>',
                        r'<script>document\.documentElement.*?<script defer src="https://analytics']:
            with self.subTest(pattern=pattern):
                self.assertEqual(self.page_part('list/index.html', pattern), self.page_part('index.html', pattern))
        self.assertIn('<script src="/site.js" defer onerror="document.documentElement.classList.remove(\'js\')"></script>',
                      (ROOT / 'list/index.html').read_text())

        page = self.open(self.context(reduced_motion='reduce'), 'list/')
        self.assertEqual(page.locator('h1').count(), 1)
        self.assertEqual(page.locator('.masthead__name').evaluate('el => el.tagName'), 'H1')
        self.assertEqual(page.locator('link[rel="canonical"]').get_attribute('href'), 'https://spidleweb.net/list/')
        self.assertEqual(page.locator('.masthead__places a[aria-current="page"]').text_content(), 'Craft')
        current = 'els => els.map(el => [el.getAttribute("href"), el.getAttribute("aria-current")])'
        self.assertEqual(page.locator('.view-switch a').evaluate_all(current), [['/', None], ['/list/', 'page']])
        self.assertEqual(page.locator('.view-dock a').evaluate_all(current), [['/', None], ['/list/', 'page']])
        self.assertEqual(page.locator('.legend__item').evaluate_all(current),
                         [['/', None], ['/list/', 'page'], ['/work/', None]])
        switch = page.locator('.view-switch').bounding_box()
        self.assertAlmostEqual(switch['x'] + switch['width'] / 2, 720, delta=1)
        self.assertTrue(page.locator('.craft-head__line').is_visible())
        self.assertTrue(page.locator('[data-filters]').is_visible())
        # Grid in the switcher goes back to the Grid.
        page.locator('.view-switch a[href="/"]').click()
        page.wait_for_url(f'{ORIGIN}/')
        self.assertEqual(page.locator('.view-switch a[aria-current="page"]').get_attribute('href'), '/')
        self.assertEqual(page.errors, [])
        page = self.open(self.context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True), 'list/')
        self.assertEqual(page.locator('.masthead__trigger').text_content(), 'Menu, Craft')
        self.assertEqual(page.locator('.view-switch').bounding_box()['width'], 358)

    def test_list_runs_two_columns_on_desktop_and_one_on_phones(self):
        # Row 09: 660 by 400 frames in two columns at 1440, and 358 by 254 in
        # one column at 390, each image above its rule, title, and note.
        for width, columns, frame in [(1440, 2, (660, 400)), (1024, 2, None), (768, 2, None),
                                      (390, 1, (358, 254)), (320, 1, None)]:
            with self.subTest(width=width):
                page = self.open(self.context(viewport={'width': width, 'height': 900}, reduced_motion='reduce'), 'list/')
                rows = page.evaluate("""() => [...document.querySelectorAll('.stream-row:not([hidden])')].map(el => {
                  const media = el.querySelector('.stream-row__media').getBoundingClientRect();
                  const body = el.querySelector('.stream-row__body');
                  return {id: el.id, left: Math.round(el.getBoundingClientRect().left),
                          top: Math.round(el.getBoundingClientRect().top + scrollY),
                          frame: [Math.round(media.width), Math.round(media.height)],
                          stacked: media.bottom <= body.getBoundingClientRect().top,
                          rule: parseFloat(getComputedStyle(body).borderTopWidth)};
                })""")
                self.assertEqual(len({row['left'] for row in rows}), columns)
                for i in range(0, len(rows) - len(rows) % columns, columns):
                    self.assertEqual(len({row['top'] for row in rows[i:i + columns]}), 1, rows[i]['id'])
                self.assertTrue(all(row['stacked'] and row['rule'] == 3 for row in rows))
                if frame:
                    self.assertEqual(tuple(rows[0]['frame']), frame)
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                if width == 1440:
                    # The title's link covers the row, and the row's own links sit above it.
                    hit = """([x, y]) => { const a = document.elementFromPoint(x, y).closest('a');
                      return a && (a.dataset.open || a.getAttribute('href')); }"""
                    media = page.locator('#expert-insights .stream-row__media').bounding_box()
                    self.assertEqual(page.evaluate(hit, [media['x'] + media['width'] / 2, media['y'] + media['height'] / 2]),
                                     'expert-insights')
                    action = page.locator('#expert-insights .stream-row__action').bounding_box()
                    self.assertEqual(page.evaluate(hit, [action['x'] + action['width'] / 2, action['y'] + action['height'] / 2]),
                                     '/work/expert-insights')
                self.assertEqual(page.errors, [])
                page.close()

    def test_list_opens_an_item_under_its_pair(self):
        # Either item of a pair opens under the pair, with the rise under the
        # item itself. On a phone the row is the pair, and it drops its hairline.
        for width, index, end in [(1440, 4, 5), (1440, 5, 5), (390, 5, 5)]:
            with self.subTest(width=width, index=index):
                context = self.context(viewport={'width': width, 'height': 900}, is_mobile=width < 600,
                                       has_touch=width < 600)
                page = self.open(context, 'list/')
                ids = self.item_ids(page, '.stream-list > .stream-row')
                self.open_item(page, ids[index])
                state = self.panel_state(page)
                self.assertEqual((state['prev'], state['next'], state['opener']), (ids[end], ids[end + 1], ids[index]))
                self.assertEqual((state['left'], state['width']), (0, state['viewport']))
                self.assertAlmostEqual(state['peak'], state['openerCentre'], delta=0.6)
                self.assertEqual(page.locator(f'#{ids[index]} .stream-row__link').get_attribute('aria-expanded'), 'true')
                if width < 600:
                    self.assertEqual(page.locator(f'#{ids[index]}').evaluate('el => getComputedStyle(el).borderBottomWidth'), '0px')
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                page.keyboard.press('Escape')
                page.wait_for_function("() => !document.querySelector('.stream-panel')")
                self.assertEqual(page.evaluate('document.activeElement.dataset.open'), ids[index])
                self.assertEqual(page.errors, [])
                page.close()
        # The image opens the item too, and a row's own link leaves for its page.
        def click_image(page, item_id):
            box = page.locator(f'#{item_id} .stream-row__media').bounding_box()
            page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)

        page = self.open(self.context(), 'list/')
        click_image(page, 'expert-insights')
        self.wait_for_panel(page, 'expert-insights')
        page.keyboard.press('Escape')
        page.locator('#expert-insights .stream-row__action').click()
        page.wait_for_url(f'{ORIGIN}/work/expert-insights')
        # Without JavaScript the title's link goes to the item's page.
        page = self.open(self.context(java_script_enabled=False), 'list/')
        self.assertTrue(page.locator('.stream-row').first.is_visible())
        page.locator('#fields-on-the-map').scroll_into_view_if_needed()
        click_image(page, 'fields-on-the-map')
        page.wait_for_url(f'{ORIGIN}/work/conservis#fig-conservis-03')

    def test_list_filters_pagination_and_deep_links_follow_the_grid(self):
        context = self.context(reduced_motion='reduce')
        grid = self.open(context)
        order = [card['id'] for card in self.craft_cards(grid)]
        grid.close()
        page = self.open(context, 'list/')
        rows = self.list_rows(page)
        self.assertEqual([row['id'] for row in rows], order)
        total = len(rows)
        shown = min(30, total)
        self.assertEqual(page.locator('.stream-row:not([hidden])').count(), shown)
        self.assertEqual(page.locator('.pager__count').text_content(), f'{shown} of {total} items')
        # Right-aligned at the edge of the last column.
        pager = page.locator('[data-pager]').bounding_box()
        last = page.locator('.stream-row').nth(1).bounding_box()
        self.assertAlmostEqual(pager['x'] + pager['width'], last['x'] + last['width'], delta=1)
        page.locator('.pager__more').click()
        self.assertEqual(page.locator('.stream-row:not([hidden])').count(), min(60, total))
        self.assertEqual(page.evaluate('document.activeElement.closest("article")?.id'), rows[shown]['id'])
        page.reload()
        self.settle(page)
        self.assertEqual(page.locator('.stream-row:not([hidden])').count(), min(60, total))

        page = self.open(context, 'list/')
        page.locator('select[data-filter="type"]').select_option('prototype')
        prototypes = [row for row in rows if row['type'] == 'prototype']
        self.assertEqual(page.locator('.stream-row:not([hidden])').count(), min(30, len(prototypes)))
        self.assertTrue(page.url.endswith('/list/?type=prototype'))
        industry = prototypes[0]['industry']
        page.locator('select[data-filter="industry"]').select_option(industry)
        self.assertEqual(page.locator('.stream-row:not([hidden])').count(),
                         sum(row['industry'] == industry for row in prototypes))
        page.goto(f'{ORIGIN}/list/?type=reel&industry=finance')
        self.settle(page)
        self.assertTrue(page.locator('[data-stream-empty]').is_visible())
        page.locator('[data-filters-clear]').click()
        self.assertEqual(page.locator('.stream-row:not([hidden])').count(), shown)

        # A link deep into the List reveals everything up to its row and opens it.
        page = self.open(context, f'list/#{order[-1]}')
        self.wait_for_panel(page, order[-1])
        self.assertEqual(page.locator('.stream-row:not([hidden])').count(), total)
        self.assertEqual(self.panel_state(page)['opener'], order[-1])
        self.assertEqual(page.errors, [])

    def test_phones_drop_try_it_for_prototypes_that_are_not_mobile(self):
        # Jason's ruling of 2026-09-24: a phone offers only a Mobile prototype
        # live, so the rest drop Try it, in the Grid and in the List.
        for path, block in [('index.html', 'stream-card'), ('list/', 'stream-row')]:
            for width in [1440, 390]:
                with self.subTest(path=path, width=width):
                    page = self.open(self.context(viewport={'width': width, 'height': 900}), path)
                    island = page.evaluate("JSON.parse(document.getElementById('stream-data').textContent).items")
                    platforms = page.locator(f'.{block}').evaluate_all('els => els.map(el => [el.id, el.dataset.platform || null])')
                    for item_id, platform in platforms:
                        expected = island[item_id].get('platform')
                        self.assertEqual(platform, expected.lower() if expected else None, item_id)
                    badges = page.locator(f'.{block}[data-type="prototype"]').evaluate_all(f"""els => els.map(el =>
                      [el.dataset.platform, getComputedStyle(el.querySelector('.{block}__badge')).display !== 'none'])""")
                    self.assertTrue({platform for platform, _ in badges} >= {'mobile', 'web'})
                    for platform, shown in badges:
                        self.assertEqual(shown, width >= 600 or platform == 'mobile', platform)
                    if block == 'stream-row':
                        hints = page.locator('.stream-row[data-type="prototype"]').evaluate_all("""els => els.map(el => {
                          const hint = el.querySelector('.stream-row__hint');
                          const shown = parseFloat(getComputedStyle(hint).fontSize) ? hint.textContent
                            : getComputedStyle(hint, '::before').content;
                          return [el.dataset.platform, shown];
                        })""")
                        for platform, hint in hints:
                            self.assertIn('Try it here' if width >= 600 or platform == 'mobile' else 'Open', hint)
                    page.close()

    def test_redirects_and_sitemap_carry_the_new_routes(self):
        # The test origin does not apply _redirects, so this reads the files.
        # Pages takes one rule a line: source, destination, status.
        rules = [line.split() for line in (ROOT / '_redirects').read_text().splitlines()
                 if line.strip() and not line.lstrip().startswith('#')]
        self.assertTrue(all(len(rule) == 3 for rule in rules), rules)
        self.assertIn(['/feed/', '/', '301'], rules)
        self.assertIn(['/feed', '/', '301'], rules)
        self.assertFalse((ROOT / 'feed').exists())

        namespace = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = ElementTree.parse(ROOT / 'sitemap.xml').getroot().findall('s:url', namespace)
        locs = [url.find('s:loc', namespace).text for url in urls]
        expected = ['/', '/list/', '/work/', *[f'/work/{slug}' for slug in WORK_ORDER],
                    '/writing/', '/writing/how-i-built-description-generator']
        self.assertEqual(sorted(locs), sorted(f'https://spidleweb.net{path}' for path in expected))
        for url in urls:
            self.assertRegex(url.find('s:lastmod', namespace).text, r'^\d{4}-\d{2}-\d{2}$')
        # Every page listed is served, and names itself as the canonical URL.
        context = self.context(java_script_enabled=False)
        for loc in locs:
            with self.subTest(loc=loc):
                page = context.new_page()
                response = page.goto(loc.replace('https://spidleweb.net', ORIGIN))
                self.assertEqual(response.status, 200)
                self.assertEqual(page.locator('link[rel="canonical"]').get_attribute('href'), loc)
                page.close()

    def test_not_found_page_carries_the_chrome_with_no_place_current(self):
        # Pages serves 404.html at whatever address was missing, so every link
        # and asset must be root-relative.
        for target in re.findall(r'(?:href|src)="([^"]+)"', (ROOT / '404.html').read_text()):
            self.assertRegex(target, r'^(/|#|https://|mailto:)', target)
        # About and the thin footer line are the site's, word for word.
        for pattern in [r'<section class="about".*?</section>', r'<footer class="site-footer">.*?</footer>']:
            self.assertEqual(self.page_part('404.html', pattern), self.page_part('work/index.html', pattern))
        for width in [1440, 390]:
            with self.subTest(width=width):
                phone = width < 600
                page = self.open(self.context(viewport={'width': width, 'height': 900}, is_mobile=phone,
                                              has_touch=phone, reduced_motion='reduce'), '404.html')
                self.assertEqual(page.locator('h1').inner_text().lower(), 'page not found')
                self.assertIn('That page is not here.', page.locator('main').inner_text())
                self.assertEqual(page.locator('[aria-current]').count(), 0)
                self.assertEqual(page.locator('.legend, .view-switch').count(), 0)
                self.assertTrue(page.locator('.footline .email').is_visible())
                if phone:
                    self.assertEqual(page.locator('.masthead__trigger').text_content(), 'Menu')
                    page.locator('.masthead__trigger').tap()
                    self.assertEqual(page.locator('#site-places a:visible').count(), 4)
                # About opens in place, as on every page.
                page.locator('.masthead__places a[href="#about"]').click()
                page.wait_for_function("() => !document.getElementById('about').hidden")
                self.assertTrue(page.locator('#about').is_visible())
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                self.assertEqual(page.errors, [])
                page.close()

    def test_next_story_band_moves_forward_and_wraps_in_work_order(self):
        # Replaces the endpaper cycle test: the band is forward only, follows
        # /work/ order, and wraps from the last case study to the first.
        context = self.context(reduced_motion='reduce')
        themes = {}
        for slug in WORK_ORDER:
            page = self.open(context, f'work/{slug}')
            themes[slug] = page.evaluate("""() => ({
              dark: getComputedStyle(document.querySelector('.case-context__title')).color,
              paper: getComputedStyle(document.body).backgroundColor
            })""")
            page.close()
        page = self.open(context, 'work/')
        self.assertEqual(page.locator('.entry__link').evaluate_all('els => els.map(el => el.getAttribute("href"))'),
                         [f'/work/{slug}' for slug in WORK_ORDER])
        page.locator('.entry__link').first.click()
        visited = []
        for i, slug in enumerate(WORK_ORDER):
            page.wait_for_url(f'{ORIGIN}/work/{slug}')
            visited.append(slug)
            destination = WORK_ORDER[(i + 1) % len(WORK_ORDER)]
            band = page.locator('.next-story')
            self.assertEqual(band.count(), 1)
            self.assertEqual(band.get_attribute('aria-label'), 'Next case study')
            # One link and nothing else: no way back to /work/ or home.
            self.assertEqual(band.locator('a').count(), 1)
            self.assertEqual(page.locator('.case-endpaper, a:text-is("Back to all work")').count(), 0)
            actual = band.evaluate("""el => ({
              bg: getComputedStyle(el, '::before').backgroundColor,
              fg: getComputedStyle(el).color,
              paper: getComputedStyle(document.body).backgroundColor,
              slope: getComputedStyle(el, '::before').clipPath
            })""")
            self.assertEqual(actual['bg'], themes[destination]['dark'])
            self.assertEqual(actual['fg'], themes[destination]['paper'])
            self.assertEqual(actual['paper'], themes[slug]['paper'])
            self.assertIn('48px', actual['slope'])
            link = band.locator('.next-story__link')
            self.assertEqual(link.get_attribute('href'), f'/work/{destination}')
            self.assertGreaterEqual(link.bounding_box()['height'], 44)
            link.focus()
            self.assertEqual(link.evaluate('el => getComputedStyle(el).outlineStyle'), 'solid')
            page.keyboard.press('Enter')
        page.wait_for_url(f'{ORIGIN}/work/{WORK_ORDER[0]}')
        self.assertEqual(visited, WORK_ORDER)
        self.assertEqual(page.errors, [])

    def test_case_context_sticks_only_when_it_fits_and_stops_before_the_ending(self):
        # The ending is now More from, when a case study shares anything, then
        # the next-story band; the rail stops at the end of the case layout.
        context = self.context(reduced_motion='reduce')
        for path in CASE_PAGES:
            page = self.open(context, path)
            rail = page.locator('.case-context')
            self.assertEqual(rail.evaluate('el => getComputedStyle(el).position'), 'sticky')
            page.evaluate('scrollTo(0, 1000)')
            self.settle(page)
            self.assertAlmostEqual(rail.bounding_box()['y'], 24, delta=1)
            page.locator('.next-story').scroll_into_view_if_needed()
            self.settle(page)
            bounds = rail.bounding_box()
            end = page.evaluate("""() => {
              const next = [...document.querySelectorAll('main ~ *')].find(el => el.getClientRects().length);
              return next.getBoundingClientRect().top;
            }""")
            self.assertLessEqual(bounds['y'] + bounds['height'], end)
            for width, height in [(1440, 400), (834, 1112), (390, 844), (320, 844)]:
                page.set_viewport_size({'width': width, 'height': height})
                self.settle(page)
                self.assertEqual(rail.evaluate('el => getComputedStyle(el).position'), 'static')
            page.set_viewport_size({'width': 1440, 'height': 900})
            page.add_style_tag(content='.case-context { font-size: 200%; } .case-context p, .case-context dd { font-size: inherit; }')
            page.wait_for_function("getComputedStyle(document.querySelector('.case-context')).position === 'static'")
            page.close()
        page = self.open(self.context(java_script_enabled=False), 'work/everag.html')
        self.assertEqual(page.locator('.case-context').evaluate('el => getComputedStyle(el).position'), 'static')

    def test_case_proofs_fonts_and_keyboard_links(self):
        context = self.context(reduced_motion='reduce')
        for path in CASE_PAGES:
            page = self.open(context, path)
            count = page.locator('.case-proofs img').count()
            self.assertGreaterEqual(count, 4 if path == 'work/campaign-sim.html' else 5)
            self.assertLessEqual(count, 11)
            page.evaluate("""async () => {
              for (const image of document.images) image.loading = 'eager';
              await Promise.all([...document.images].map(image => image.decode()));
            }""")
            self.assertTrue(page.locator('.case-proofs img').evaluate_all("""images => images.every(img => {
              const box = img.getBoundingClientRect();
              const ratio = Number(img.getAttribute('width')) / Number(img.getAttribute('height'));
              return img.complete && img.naturalWidth > 0 && img.alt.trim() &&
                Math.abs(box.width / box.height - ratio) < 0.01 && getComputedStyle(img).filter === 'none';
            })"""))
            cdp = context.new_cdp_session(page)
            cdp.send('DOM.enable'); cdp.send('CSS.enable')
            root = cdp.send('DOM.getDocument')['root']['nodeId']
            for selector, family in [('.case-context__title', 'GTAmerica-ExpandedRegular'),
                                     ('.case-context__note', 'EB Garamond'), ('.proof figcaption', 'EB Garamond')]:
                node = cdp.send('DOM.querySelector', {'nodeId': root, 'selector': selector})['nodeId']
                fonts = cdp.send('CSS.getPlatformFontsForNode', {'nodeId': node})['fonts']
                self.assertTrue(any((font['familyName'] == family or font['postScriptName'] == family) and font['isCustomFont'] for font in fonts), (path, selector, fonts))
            # Complete-word checks catch a trailing letter stranded in a title even without overflow.
            self.assertTrue(page.locator('h1').evaluate("""el => {
              const text = el.firstChild;
              return el.textContent.split(' ').every(word => {
                const start = text.textContent.indexOf(word); const range = document.createRange();
                range.setStart(text, start); range.setEnd(text, start + word.length);
                return range.getClientRects().length === 1;
              });
            }"""), path)
            page.locator('.skip-link').focus()
            page.keyboard.press('Tab')
            self.assertEqual(page.locator(':focus').evaluate('el => el.closest(".masthead__name") !== null'), True)
            page.keyboard.press('Tab')
            self.assertEqual(page.locator(':focus').text_content(), 'Craft')
            self.assertEqual(page.locator('.case-proofs a[href*="assets/"]').count(), 0)
            # Case imagery is never a link. More from cards are, by the card contract.
            self.assertEqual(page.locator('main a:has(img)').count(), 0)
            # Desktop captures are full-height; phone captures retain every edge inside native overflow.
            self.assertTrue(page.locator('.proof__frame').evaluate_all("""els => els.every(el => {
              const image = el.querySelector('img');
              const before = el.getBoundingClientRect();
              const phone = el.closest('.proof-phone');
              const naturalHeight = image.getBoundingClientRect().height;
              el.scrollTop = el.scrollHeight; el.scrollLeft = el.scrollWidth;
              const after = el.getBoundingClientRect(); const content = image.getBoundingClientRect();
              return (phone ? before.height === 560 : Math.abs(before.height - naturalHeight) < 1) &&
                getComputedStyle(el).aspectRatio === 'auto' && getComputedStyle(el).borderRadius === '0px' &&
                before.height === after.height && content.bottom <= after.bottom + 2 &&
                content.right <= after.right + 2;
            })"""), path)
            page.locator('source').evaluate_all('els => els.forEach(el => el.remove())')
            page.evaluate('async () => { await Promise.all([...document.images].map(img => img.decode())); }')
            self.assertEqual(page.errors, [])
            page.close()

    def test_case_phone_sequences_never_wrap_into_two_rows(self):
        context = self.context(reduced_motion='reduce')
        for slug in ['everag', 'vidscrip', 'conservis']:
            page = self.open(context, f'work/{slug}.html')
            for width in [600, 768, 834, 999, 1000, 1024, 1280, 1440, 1920]:
                page.set_viewport_size({'width': width, 'height': 900})
                self.settle(page)
                self.assertTrue(page.locator('.proof-phones').evaluate_all("""groups => groups.every(group => {
                  const phones = [...group.querySelectorAll('.proof-phone')].map(el => el.getBoundingClientRect());
                  const stacked = getComputedStyle(group).flexDirection === 'column';
                  return group.scrollWidth <= group.clientWidth && phones.every((box, i) =>
                    box.width >= 239 && (stacked ? Math.abs(box.x - phones[0].x) < 1 &&
                    (!i || box.y > phones[i - 1].bottom) : Math.abs(box.y - phones[0].y) < 1));
                })"""), (slug, width))
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
            for width in [390, 320]:
                page.set_viewport_size({'width': width, 'height': 844})
                self.settle(page)
                self.assertTrue(page.locator('.proof-phones').evaluate_all("""groups => groups.every(group => {
                  const phones = [...group.querySelectorAll('.proof-phone')].map(el => el.getBoundingClientRect());
                  return phones.every((box, i) => Math.abs(box.x - phones[0].x) < 1 && (!i || box.y > phones[i - 1].bottom));
                })"""))
            page.close()

    def test_case_captures_scroll_with_keyboard_and_without_javascript(self):
        for options in [{'reduced_motion': 'reduce'}, {'java_script_enabled': False}, {'block_script': True}]:
            context = self.context(**options)
            for slug in ['everag', 'vidscrip']:
                page = self.open(context, f'work/{slug}.html')
                capture = page.locator('.proof-phone .proof__frame').first
                capture.locator('img').evaluate('img => img.decode()')
                capture.focus()
                y = page.evaluate('scrollY')
                page.keyboard.press('End')
                # Page RAF polling is suspended when JavaScript is disabled.
                deadline = time.monotonic() + 2
                while capture.evaluate('el => el.scrollTop') <= 50 and time.monotonic() < deadline:
                    page.wait_for_timeout(50)
                self.assertGreater(capture.evaluate('el => el.scrollTop'), 50, (slug, options))
                self.assertEqual(page.evaluate('scrollY'), y)
                if options.get('java_script_enabled') is False or options.get('block_script'):
                    self.assertEqual(capture.locator('img').evaluate('el => getComputedStyle(el).filter'), 'none')
                page.close()
        for width in [1440, 390]:
            page = self.open(self.context(viewport={'width': width, 'height': 900}, reduced_motion='reduce'), 'work/vidscrip.html')
            capture = page.locator('.proof-phone .proof__frame').first
            capture.scroll_into_view_if_needed()
            bounds = capture.bounding_box()
            self.assertEqual(bounds['height'], 480 if width <= 768 else 560)
            y = page.evaluate('scrollY')
            image_bounds = capture.locator('img').bounding_box()
            page.mouse.move(bounds['x'] + bounds['width'] / 2, bounds['y'] + bounds['height'] / 2)
            page.mouse.wheel(0, 200)
            page.wait_for_function('el => el.scrollTop >= 190', arg=capture.element_handle())
            self.assertEqual(page.evaluate('scrollY'), y)
            after = capture.locator('img').bounding_box()
            self.assertEqual((after['width'], after['height']), (image_bounds['width'], image_bounds['height']))

    def test_case_color_reveals_at_frame_midpoint_once_and_respects_reduced_motion(self):
        for height in [900, 260]:
            page = self.open(self.context(viewport={'width': 1440, 'height': height}), 'work/everag.html')
            frame = page.locator('.proof__frame').nth(1)
            trigger = frame.evaluate('el => scrollY + el.getBoundingClientRect().top + el.offsetHeight / 2 - innerHeight')
            page.evaluate('y => scrollTo(0, y)', trigger - 2)
            self.settle(page)
            self.assertNotIn('is-color', frame.get_attribute('class'))
            self.assertEqual(frame.locator('img').evaluate('el => getComputedStyle(el).filter'), 'grayscale(1)')
            # Hover cannot reveal a frame before its scroll threshold.
            page.mouse.move(900, height - 4)
            self.settle(page)
            self.assertNotIn('is-color', frame.get_attribute('class'))
            page.evaluate('y => scrollTo(0, y)', trigger + 2)
            page.wait_for_function('el => el.classList.contains("is-color")', arg=frame.element_handle())
            page.wait_for_function('el => getComputedStyle(el).filter === "none"', arg=frame.locator('img').element_handle())
            page.evaluate('scrollTo(0, 0)')
            self.settle(page)
            self.assertIn('is-color', frame.get_attribute('class'))
            page.emulate_media(reduced_motion='reduce')
            page.wait_for_function("!document.documentElement.classList.contains('color-reveal-active')")
            self.assertTrue(page.locator('.proof__frame img').evaluate_all("els => els.every(el => getComputedStyle(el).filter === 'none' && getComputedStyle(el).transitionDuration === '0s')"))
            page.emulate_media(reduced_motion='no-preference')
            self.assertTrue(page.locator('.proof__frame img').evaluate_all("els => els.every(el => getComputedStyle(el).filter === 'none')"))
            page.close()

    def test_case_navigation_links_change_only_color_and_follow_destination_palette(self):
        context = self.context(reduced_motion='reduce')
        hover_colors = {}
        band_colors = []
        for path in CASE_PAGES:
            page = self.open(context, path)
            # The page's own hover tint, resolved to a computed colour.
            hover_colors[f'/work/{Path(path).stem}'] = page.evaluate("""() => {
              const probe = document.body.appendChild(document.createElement('span'));
              probe.style.color = 'var(--case-hover)';
              const color = getComputedStyle(probe).color; probe.remove(); return color;
            }""")
            for selector in ['.case-context__links a', '.next-story a']:
                for link in page.locator(selector).all():
                    page.mouse.move(0, 0)
                    before = link.evaluate('el => ({color: getComputedStyle(el).color, bg: getComputedStyle(el).backgroundColor})')
                    link.hover()
                    after = link.evaluate('el => ({color: getComputedStyle(el).color, bg: getComputedStyle(el).backgroundColor, decoration: getComputedStyle(el).textDecorationLine})')
                    self.assertNotEqual(before['color'], after['color'])
                    self.assertNotEqual(after['color'], 'rgb(250, 25, 0)')
                    self.assertEqual(after['bg'], before['bg'])
                    self.assertEqual(after['decoration'], 'none')
                    if selector == '.next-story a':
                        band_colors.append((link.get_attribute('href'), after['color']))
            page.close()
        self.assertEqual(len(set(hover_colors.values())), 6)
        self.assertEqual(len(band_colors), 6)
        for destination, color in band_colors:
            self.assertEqual(color, hover_colors[destination])
        page = self.open(self.context(reduced_motion='reduce'), 'work/expert-insights.html')
        for i in [5, 6, 7]:
            image = page.locator(f'img[src$="expert-insights-0{i}-full.png"]')
            self.assertEqual(image.count(), 1)
            self.assertEqual(image.get_attribute('width'), '2880')
            self.assertEqual(image.get_attribute('height'), '2048')

    # ---- Work and Writing pages (Phase 2C) ----

    def case_facts(self, slug):
        """The first figure's image and the role and dates on a case-study page."""
        html = (ROOT / f'work/{slug}.html').read_text(encoding='utf-8')
        first = re.search(r'<figure[^>]*>[\s\S]*?<img src="\.\./([^"]+)"', html).group(1)
        facts = [re.sub(r'<[^>]+>', '', dd) for dd in re.findall(r'<dd>([\s\S]*?)</dd>', html)]
        return {'cover': f'/{first}', 'role': facts[0], 'dates': facts[1]}

    def test_work_and_writing_pages_carry_the_chrome_and_mark_their_place(self):
        places = {**{path: 'Work' for path in [*CASE_PAGES, 'work/index.html']},
                  **{path: 'Writing' for path in READING_PAGES if path.startswith('writing/')}}
        for width in [1440, 390]:
            context = self.context(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
            for path, place in places.items():
                with self.subTest(width=width, path=path):
                    page = self.open(context, path)
                    # The page keeps its own h1; the name is a plain link home.
                    self.assertEqual(page.locator('.masthead h1').count(), 0)
                    self.assertEqual(page.locator('.masthead__name a').get_attribute('href'), '/')
                    current = page.locator('.masthead__places [aria-current="page"]')
                    self.assertEqual(current.count(), 1)
                    self.assertEqual(current.text_content(), place)
                    self.assertEqual(page.locator('.masthead__trigger').text_content(), f'Menu, {place}')
                    # Body order: masthead, About, then main, and the thin line ends the page.
                    order = page.evaluate("""() => [...document.body.children].map(el => el.matches('.masthead') ? 'masthead'
                      : el.matches('.about') ? 'about' : el.matches('main') ? 'main' : el.matches('.site-footer') ? 'footer' : null).filter(Boolean)""")
                    self.assertEqual(order, ['masthead', 'about', 'main', 'footer'])
                    self.assertEqual(page.locator('.legend, .view-switch, .case-masthead, .case-endpaper').count(), 0)
                    self.assertTrue(page.locator('.footline').is_visible())
                    self.assertEqual(page.evaluate("document.documentElement.classList.contains('js')"), True)
                    # The page's first line sits where Paper puts it.
                    first = page.locator('.page-head__title, .post__kicker, .case-context__title').first.bounding_box()
                    masthead = page.locator('.masthead').bounding_box()
                    self.assertGreater(first['y'], masthead['y'] + masthead['height'])
                    if width == 390:
                        page.locator('.masthead__trigger').click()
                        self.assertTrue(current.is_visible())
                        dot = current.evaluate("el => getComputedStyle(el, '::before').backgroundColor")
                        self.assertEqual(dot, 'rgb(250, 25, 0)')
                        page.keyboard.press('Escape')
                    self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                    self.assertEqual(page.errors, [])
                    page.close()

    def test_work_index_lists_case_studies_newest_first_as_whole_row_links(self):
        for width in [1440, 390]:
            page = self.open(self.context(viewport={'width': width, 'height': 900}, reduced_motion='reduce'), 'work/')
            with self.subTest(width=width):
                # The head is the title and its rule: no intro line, no numbering.
                self.assertEqual(page.locator('h1').text_content(), 'Work')
                self.assertEqual(page.locator('.page-head > *').count(), 1)
                self.assertIsNone(re.search(r'\b0[1-6]\b', page.locator('main').inner_text()))
                headings = page.evaluate("""() => [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')]
                  .filter(el => el.getClientRects().length).map(el => Number(el.tagName[1]))""")
                self.assertEqual(headings, [1, 2, 2, 2, 2, 2, 2])
                entries = page.locator('.entry')
                self.assertEqual(entries.count(), len(WORK_ORDER))
                colors = set()
                for i, slug in enumerate(WORK_ORDER):
                    entry = entries.nth(i)
                    facts = self.case_facts(slug)
                    # The whole row is one link, named by its title.
                    self.assertEqual(entry.locator('a').count(), 1)
                    link = entry.locator('.entry__link')
                    self.assertEqual(link.get_attribute('href'), f'/work/{slug}')
                    title = link.locator('.entry__title').text_content()
                    self.assertEqual(page.get_by_role('link', name=title, exact=True).count(), 1)
                    for part in ['.entry__cover', '.entry__title', '.entry__dek', '.entry__meta', '.entry__cta']:
                        self.assertEqual(link.locator(part).count(), 1, (slug, part))
                    self.assertEqual(link.locator('.entry__cta').text_content().strip(), 'Read the case study →')
                    self.assertEqual(link.locator('.entry__dateline').text_content(), facts['dates'])
                    self.assertEqual(link.locator('.entry__detail').text_content(), facts['role'])
                    # The cover is the page's first figure, on a slab of the project colour.
                    cover = link.locator('.entry__cover img')
                    self.assertEqual(cover.get_attribute('src'), facts['cover'])
                    self.assertEqual(cover.get_attribute('alt'), '')
                    self.assertTrue(cover.evaluate('async img => { img.loading = "eager"; await img.decode(); return img.naturalWidth > 0; }'))
                    look = link.evaluate("""el => ({
                      title: getComputedStyle(el.querySelector('.entry__title')).color,
                      slab: getComputedStyle(el.querySelector('.entry__cover'), '::before').backgroundColor,
                      dek: getComputedStyle(el.querySelector('.entry__dek')).color
                    })""")
                    self.assertEqual(look['title'], look['slab'])
                    self.assertEqual(look['dek'], 'rgb(10, 10, 10)')
                    colors.add(look['title'])
                    box, cover_box, title_box = link.bounding_box(), cover.bounding_box(), link.locator('.entry__title').bounding_box()
                    self.assertGreaterEqual(box['height'], 44)
                    if width == 1440:
                        self.assertLess(cover_box['x'] + cover_box['width'], title_box['x'])
                        cta = link.locator('.entry__cta').bounding_box()
                        self.assertAlmostEqual(cta['x'] + cta['width'], box['x'] + box['width'], delta=1)
                    else:
                        self.assertLessEqual(cover_box['y'] + cover_box['height'], title_box['y'])
                        self.assertGreater(cover_box['width'], width - 60)
                self.assertEqual(len(colors), len(WORK_ORDER))
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                page.locator('.entry__link').first.focus()
                focused = page.locator(':focus')
                self.assertEqual(focused.get_attribute('href'), f'/work/{WORK_ORDER[0]}')
                self.assertEqual(focused.evaluate('el => getComputedStyle(el).outlineStyle'), 'solid')
                self.assertEqual(page.errors, [])
            page.close()

    def test_figure_anchors_follow_image_names_and_land_on_their_figure(self):
        for path in CASE_PAGES:
            html = (ROOT / path).read_text(encoding='utf-8')
            ids = []
            for figure in re.findall(r'<figure[^>]*>[\s\S]*?</figure>', html):
                anchor = re.match(r'<figure[^>]*\sid="([^"]+)"', figure)
                image = re.search(r'<img src="([^"]+)"', figure).group(1)
                self.assertIsNotNone(anchor, (path, image))
                self.assertEqual(anchor.group(1), f'fig-{Path(image).stem}', path)
                ids.append(anchor.group(1))
            self.assertGreater(len(ids), 0)
            self.assertEqual(len(ids), len(set(ids)), path)
        # Every stream item that names a figure lands on it, with room above.
        stream = json.loads((ROOT / 'content/stream.json').read_text(encoding='utf-8'))
        linked = [item['caseStudy'] for item in stream if item.get('caseStudy', {}).get('figure')]
        self.assertGreater(len(linked), 0)
        context = self.context(reduced_motion='reduce')
        for case in linked:
            with self.subTest(figure=case['figure']):
                page = self.open(context, f'work/{case["slug"]}#fig-{case["figure"]}')
                target = page.locator(f'#fig-{case["figure"]}')
                self.assertEqual(target.evaluate('el => el.tagName'), 'FIGURE')
                self.assertAlmostEqual(target.bounding_box()['y'], 24, delta=2)
                page.close()

    def test_more_from_gathers_what_each_case_study_shares(self):
        stream = json.loads((ROOT / 'content/stream.json').read_text(encoding='utf-8'))
        for width in [1440, 390]:
            context = self.context(viewport={'width': width, 'height': 900}, reduced_motion='reduce')
            for path in CASE_PAGES:
                slug = Path(path).stem
                expected = [item['id'] for item in stream if item.get('caseStudy', {}).get('slug') == slug
                            and item['type'] != 'case-study' and not item['caseStudy'].get('figure')]
                with self.subTest(width=width, slug=slug):
                    page = self.open(context, f'work/{slug}')
                    section = page.locator('.more-from')
                    self.assertEqual(section.locator('article.stream-card').evaluate_all('els => els.map(el => el.id)'), expected)
                    # An empty section hides, heading and all.
                    self.assertEqual(section.is_visible(), bool(expected))
                    self.assertEqual(page.get_by_role('heading', name=re.compile('^More from')).count(), 1 if expected else 0)
                    headings = page.evaluate("""() => [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')]
                      .filter(el => el.getClientRects().length).map(el => Number(el.tagName[1]))""")
                    self.assertEqual(headings, [1] + ([2] + [3] * len(expected) if expected else []))
                    island = json.loads(page.locator('#stream-data').text_content())
                    self.assertTrue(set(expected) <= set(island['items']))
                    # The page's gutter matches the site's: 16px on a phone.
                    self.assertEqual(page.locator('h1').bounding_box()['x'], 40 if width == 1440 else 16)
                    if expected:
                        cards = section.locator('article.stream-card')
                        boxes = [cards.nth(i).bounding_box() for i in range(min(cards.count(), 3))]
                        per_row = 3 if width == 1440 else 2
                        first_row = [b for b in boxes if abs(b['y'] - boxes[0]['y']) < 1]
                        self.assertEqual(len(first_row), min(per_row, len(expected)))
                        if width == 1440:
                            self.assertAlmostEqual(boxes[0]['width'], (1440 - 160) / 5, delta=1)
                        for link in section.locator('.stream-card__link').all():
                            self.assertNotRegex(link.get_attribute('href'), f'^/work/{slug}#')
                    self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                    self.assertEqual(page.errors, [])
                    page.close()

    def test_writing_index_marks_its_placeholder_and_hides_it_with_one_attribute(self):
        page = self.open(self.context(reduced_motion='reduce'), 'writing/')
        self.assertEqual(page.locator('h1').text_content(), 'Writing')
        entries = page.locator('.entry')
        self.assertEqual(entries.count(), 2)
        first, placeholder = entries.nth(0), entries.nth(1)
        self.assertEqual(first.locator('a').get_attribute('href'), '/writing/how-i-built-description-generator')
        self.assertIsNone(first.get_attribute('data-placeholder'))
        self.assertEqual(placeholder.get_attribute('data-placeholder'), '')
        self.assertEqual(placeholder.locator('.entry__title').text_content(), 'Building 500+ manufacturing careers')
        for entry in [first, placeholder]:
            self.assertEqual(entry.locator('a').count(), 1)
            self.assertEqual(entry.locator('.entry__cta').text_content().strip(), 'Read the post →')
        self.assertTrue(placeholder.is_visible())
        page.locator('.entry-list').evaluate('el => el.dataset.placeholders = "hide"')
        self.assertFalse(placeholder.is_visible())
        self.assertTrue(first.is_visible())
        self.assertEqual(page.errors, [])

    def test_post_page_has_its_canonical_article_data_and_a_marked_placeholder_body(self):
        path = 'writing/how-i-built-description-generator'
        for width in [1440, 390]:
            page = self.open(self.context(viewport={'width': width, 'height': 900}, reduced_motion='reduce'), path)
            canonical = f'https://spidleweb.net/{path}'
            self.assertEqual(page.locator('link[rel="canonical"]').get_attribute('href'), canonical)
            self.assertEqual(page.locator('meta[property="og:url"]').get_attribute('content'), canonical)
            self.assertEqual(page.locator('meta[property="og:type"]').get_attribute('content'), 'article')
            data = json.loads(page.locator('script[type="application/ld+json"]').text_content())
            self.assertEqual(data['@type'], 'Article')
            self.assertEqual(data['headline'], page.locator('h1').text_content())
            self.assertEqual(data['mainEntityOfPage']['@id'], canonical)
            self.assertEqual(data['description'], page.locator('.post__dek').text_content())
            image = urlsplit(data['image'][0]).path.lstrip('/')
            self.assertTrue((ROOT / image).is_file(), image)
            self.assertEqual(page.locator('h1').count(), 1)
            self.assertEqual(page.locator('.post__kicker time').get_attribute('datetime'), '2026-09')
            self.assertTrue(page.locator('.post__cover img').evaluate('async img => { await img.decode(); return img.naturalWidth > 0 && img.alt.length > 0; }'))
            body = page.locator('.post__body')
            self.assertEqual(body.get_attribute('data-placeholder'), '')
            self.assertEqual(body.locator('.post__bars').get_attribute('aria-hidden'), 'true')
            # A post ends with the footer line, never a next-story band.
            self.assertEqual(page.locator('.next-story').count(), 0)
            self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
            self.assertEqual(page.errors, [])
            page.close()

    def test_work_and_writing_image_and_asset_paths_all_resolve(self):
        pattern = re.compile(r'(?:src|href|content)="([^"]+)"|srcset="([^"]+)"')
        for path in [*CASE_PAGES, *READING_PAGES]:
            html = (ROOT / path).read_text(encoding='utf-8')
            # The URL each page is served at, so relative paths resolve as they do live.
            base = f'https://spidleweb.net/{path.removesuffix("index.html").removesuffix(".html")}'
            checked = 0
            for single, srcset in pattern.findall(html):
                for ref in ([single] if single else [entry.split()[0] for entry in srcset.split(',')]):
                    url = urlsplit(urljoin(base, ref))
                    if url.netloc != 'spidleweb.net' or not re.search(r'\.(png|jpe?g|webp|avif|svg|woff2?|css|js)$', url.path):
                        continue
                    local = (ROOT / url.path.lstrip('/')).resolve()
                    self.assertTrue(local.is_file(), (path, ref))
                    checked += 1
            self.assertGreater(checked, 3, path)

    def test_work_pages_cross_fade_only_when_motion_is_allowed(self):
        for motion, expected in [('no-preference', True), ('reduce', False)]:
            context = self.context(reduced_motion=motion)
            context.add_init_script("addEventListener('pagereveal', event => { window.revealedWithTransition = Boolean(event.viewTransition); })")
            page = self.open(context, 'work/conservis')
            page.locator('.next-story__link').click()
            page.wait_for_url(f'{ORIGIN}/work/plinth')
            page.wait_for_function('window.revealedWithTransition !== undefined')
            self.assertEqual(page.evaluate('window.revealedWithTransition'), expected, motion)
            page.close()


    # ---- Open in place (Phase 2B): stream.js and panel.css on the fixtures ----

    GRID = 'content/fixtures/grid.html'
    LIST = 'content/fixtures/list.html'

    def open_item(self, page, item_id):
        """Click a stream card and wait for its panel to settle."""
        link = page.locator(f'.stream-card [data-open="{item_id}"], .stream-row [data-open="{item_id}"]').first
        link.scroll_into_view_if_needed()
        link.click()
        self.wait_for_panel(page, item_id)
        return link

    def wait_for_panel(self, page, item_id):
        page.wait_for_function("""id => {
          const panel = document.getElementById('stream-panel');
          return panel && !panel.classList.contains('is-moving') && location.hash === `#${id}`;
        }""", arg=item_id)
        self.settle(page)

    def panel_state(self, page):
        """Where the panel sits, what it follows, and where its rise peaks."""
        return page.evaluate("""() => {
          const panel = document.getElementById('stream-panel');
          if (!panel) return null;
          const rect = panel.getBoundingClientRect();
          const d = panel.querySelector('.stream-panel__rise path').getAttribute('d');
          const peak = d.split('C')[1].trim().split(/\\s+/).map(Number)[4];
          const opener = document.querySelector('[data-open][aria-expanded="true"]');
          const card = opener && opener.closest('.stream-card, .stream-row');
          const box = card && card.getBoundingClientRect();
          return {
            prev: panel.previousElementSibling && panel.previousElementSibling.id,
            next: panel.nextElementSibling && panel.nextElementSibling.id,
            top: rect.top + scrollY, bottom: rect.bottom + scrollY,
            left: rect.left, width: rect.width, viewport: document.documentElement.clientWidth,
            peak, opener: card && card.id, openerCentre: box && box.left + box.width / 2,
            title: panel.querySelector('#stream-panel-title').textContent.trim(),
            tone: panel.dataset.tone,
          };
        }""")

    def item_ids(self, page, selector):
        return page.eval_on_selector_all(selector, 'els => els.map(el => el.id)')

    def row_end(self, page, selector, item_id):
        """The last item sharing the given item's top edge, read from layout without a panel."""
        return page.evaluate("""([selector, id]) => {
          const items = [...document.querySelectorAll(selector)];
          const top = document.getElementById(id).getBoundingClientRect().top;
          return items.filter(el => Math.abs(el.getBoundingClientRect().top - top) < 2).pop().id;
        }""", [selector, item_id])

    def test_open_in_place_opens_under_the_row_of_the_clicked_card(self):
        cases = [
            (self.GRID, '.stream-grid > .stream-card', 1440, 6, 9),   # five columns: 7th card, row ends at the 10th
            (self.GRID, '.stream-grid > .stream-card', 390, 2, 3),    # two columns on phones
            (self.LIST, '.stream-list > .stream-row', 1440, 2, 3),    # List opens under the pair
            (self.LIST, '.stream-list > .stream-row', 390, 2, 2),     # one column on phones
        ]
        for path, selector, width, index, end in cases:
            with self.subTest(path=path, width=width):
                page = self.open(self.context(viewport={'width': width, 'height': 900}), path)
                ids = self.item_ids(page, selector)
                self.assertEqual(self.row_end(page, selector, ids[index]), ids[end])
                self.open_item(page, ids[index])
                state = self.panel_state(page)
                self.assertEqual(state['prev'], ids[end])
                self.assertEqual(state['next'], ids[end + 1])
                self.assertEqual(state['opener'], ids[index])
                # Full bleed, below the row, and the rise under the opener's centre.
                self.assertEqual((state['left'], state['width']), (0, state['viewport']))
                opener_bottom = page.locator(f'#{ids[index]}').evaluate('el => el.getBoundingClientRect().bottom + scrollY')
                self.assertGreater(state['top'], opener_bottom)
                self.assertAlmostEqual(state['peak'], state['openerCentre'], delta=0.6)
                next_top = page.locator(f'#{ids[end + 1]}').evaluate('el => el.getBoundingClientRect().top + scrollY')
                self.assertGreaterEqual(next_top, state['bottom'])
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                self.assertEqual(page.errors, [])
                page.close()

    def test_open_in_place_follows_its_card_when_the_layout_reflows(self):
        page = self.open(self.context(), self.GRID)
        selector = '.stream-grid > .stream-card'
        ids = self.item_ids(page, selector)
        self.open_item(page, ids[6])
        self.assertEqual(self.panel_state(page)['prev'], ids[9])
        # Three columns below 1100px: the 7th card's row now ends at the 9th.
        page.set_viewport_size({'width': 900, 'height': 900})
        page.wait_for_function("id => document.getElementById('stream-panel').previousElementSibling.id === id", arg=ids[8])
        self.settle(page)
        state = self.panel_state(page)
        self.assertEqual(state['opener'], ids[6])
        self.assertEqual((state['left'], state['width']), (0, 900))
        self.assertAlmostEqual(state['peak'], state['openerCentre'], delta=0.6)
        # Every row above the panel is whole.
        tops = page.eval_on_selector_all(selector, 'els => els.slice(0, 9).map(el => Math.round(el.getBoundingClientRect().top))')
        self.assertEqual(len(set(tops)), 3)
        self.assertEqual(page.errors, [])

    def test_open_in_place_escape_or_close_closes_and_returns_focus(self):
        page = self.open(self.context(), self.GRID)
        link = page.locator('.stream-card [data-open="fields-on-the-map"]')
        self.assertEqual(link.get_attribute('aria-expanded'), 'false')
        link.focus()
        page.keyboard.press('Enter')
        self.wait_for_panel(page, 'fields-on-the-map')
        self.assertEqual(link.get_attribute('aria-expanded'), 'true')
        self.assertEqual(link.get_attribute('aria-controls'), 'stream-panel')
        self.assertEqual(page.evaluate('document.activeElement.id'), 'stream-panel-title')
        self.assertEqual(page.locator('#stream-panel').get_attribute('aria-labelledby'), 'stream-panel-title')
        page.keyboard.press('Escape')
        page.wait_for_function("() => !document.querySelector('.stream-panel')")
        self.assertEqual(link.get_attribute('aria-expanded'), 'false')
        self.assertTrue(link.evaluate('el => el === document.activeElement'))
        # The visible Close button does the same, and so does the open card.
        self.open_item(page, 'fields-on-the-map')
        page.locator('#stream-panel [data-panel-close]:visible').click()
        page.wait_for_function("() => !document.querySelector('.stream-panel')")
        self.assertTrue(link.evaluate('el => el === document.activeElement'))
        self.open_item(page, 'fields-on-the-map')
        link.click()
        page.wait_for_function("() => !document.querySelector('.stream-panel')")
        self.assertEqual(page.errors, [])

    def test_open_in_place_sets_and_clears_the_hash_without_history_steps(self):
        page = self.open(self.context(), self.GRID)
        steps = page.evaluate('history.length')
        self.open_item(page, 'fields-on-the-map')
        self.assertEqual(urlsplit(page.url).fragment, 'fields-on-the-map')
        # Another card moves the panel and the address with it.
        self.open_item(page, 'weekly-activity-calendar')
        self.assertEqual(urlsplit(page.url).fragment, 'weekly-activity-calendar')
        self.assertEqual(page.locator('.stream-panel').count(), 1)
        page.keyboard.press('Escape')
        page.wait_for_function("() => !document.querySelector('.stream-panel')")
        self.assertEqual(urlsplit(page.url).fragment, '')
        self.assertEqual(page.evaluate('history.length'), steps)
        self.assertEqual(page.errors, [])

    def test_open_in_place_deep_link_reveals_the_item_and_opens_it(self):
        context = self.context()
        context.add_init_script("""window.__reveals = [];
          document.addEventListener('stream:reveal', event => window.__reveals.push(event.detail.id));""")
        page = self.open(context, f'{self.GRID}#population-forecast-matrix')
        self.wait_for_panel(page, 'population-forecast-matrix')
        self.assertEqual(page.evaluate('window.__reveals'), ['population-forecast-matrix'])
        state = self.panel_state(page)
        ids = self.item_ids(page, '.stream-grid > .stream-card')
        self.assertEqual(state['opener'], 'population-forecast-matrix')
        self.assertEqual(state['prev'], self.row_end(page, '.stream-grid > .stream-card', 'population-forecast-matrix'))
        self.assertIn(state['prev'], ids)
        # A case-study item opens in its project's band.
        self.assertEqual(state['tone'], 'band')
        self.assertIn('theme-everag', page.locator('#stream-panel').get_attribute('class'))
        self.assertEqual(page.evaluate('document.activeElement.id'), 'stream-panel-title')
        top = page.locator('#population-forecast-matrix').evaluate('el => el.getBoundingClientRect().top')
        self.assertTrue(0 <= top < 900)
        self.assertEqual(page.errors, [])
        # On a fresh load, an unknown fragment opens nothing and throws nothing.
        page = self.open(self.context(), f'{self.GRID}#not-an-item')
        page.wait_for_load_state('load')
        self.settle(page)
        self.assertEqual(page.locator('.stream-panel').count(), 0)
        self.assertEqual(page.errors, [])

    def test_open_in_place_arrow_keys_change_what_shows_but_not_where(self):
        page = self.open(self.context(), self.GRID)
        # A case study's strip: the count and caption step, the panel stays.
        self.open_item(page, 'expert-insights')
        panel = page.locator('#stream-panel')
        count = panel.locator('[data-strip-count] [aria-hidden="true"]')
        caption = panel.locator('[data-strip-caption]')
        before = self.panel_state(page)
        self.assertEqual(count.text_content(), '01 / 07')
        first_caption = caption.text_content()
        page.keyboard.press('ArrowRight')
        page.wait_for_function("() => document.querySelector('[data-strip-count] [aria-hidden]').textContent === '02 / 07'")
        page.wait_for_timeout(700)
        self.assertNotEqual(caption.text_content(), first_caption)
        track_left = panel.locator('[data-strip-track]').evaluate('el => el.scrollLeft')
        frame_left = panel.locator('.stream-strip__frame[data-index="1"]').evaluate('el => el.offsetLeft')
        self.assertAlmostEqual(track_left, frame_left, delta=1)
        after = self.panel_state(page)
        self.assertEqual((after['top'], after['prev']), (before['top'], before['prev']))
        self.assertEqual(urlsplit(page.url).fragment, 'expert-insights')
        page.keyboard.press('ArrowLeft')
        page.wait_for_function("() => document.querySelector('[data-strip-count] [aria-hidden]').textContent === '01 / 07'")
        # A neutral screen steps through its related items in the same place.
        self.open_item(page, 'weekly-activity-calendar')
        before = self.panel_state(page)
        self.assertEqual(panel.locator('.stream-related__count').text_content(), '1 of 4')
        page.keyboard.press('ArrowRight')
        page.wait_for_function("() => location.hash === '#daily-activity-schedule'")
        self.settle(page)
        after = self.panel_state(page)
        expected = page.evaluate("JSON.parse(document.getElementById('stream-data').textContent).items['daily-activity-schedule'].title")
        self.assertEqual(after['title'], expected)
        self.assertNotEqual(after['title'], before['title'])
        self.assertEqual(panel.locator('.stream-related__count').text_content(), '2 of 4')
        self.assertEqual((after['top'], after['prev'], after['opener']), (before['top'], before['prev'], before['opener']))
        self.assertAlmostEqual(after['peak'], before['peak'], delta=0.1)
        # Keys with a modifier belong to the browser.
        page.keyboard.press('Alt+ArrowLeft')
        self.settle(page)
        self.assertEqual(urlsplit(page.url).fragment, 'daily-activity-schedule')
        self.assertEqual(page.errors, [])

    def test_open_in_place_about_opens_under_the_masthead_with_the_rise(self):
        for width in (1440, 390):
            with self.subTest(width=width):
                page = self.open(self.context(viewport={'width': width, 'height': 900}), self.GRID)
                self.assertTrue(page.evaluate("document.documentElement.classList.contains('panels')"))
                about = page.locator('#about')
                self.assertFalse(about.is_visible())
                if width < 800:
                    page.locator('.masthead__trigger').click()
                link = page.locator('.masthead__places a[href="#about"]')
                link.click()
                page.wait_for_function("() => !document.getElementById('about').hidden && location.hash === '#about'")
                self.settle(page)
                self.assertEqual(page.evaluate('document.activeElement.id'), 'about-title')
                rise = page.locator('#about').evaluate("""el => {
                  const svg = el.previousElementSibling;
                  const d = svg.querySelector('path').getAttribute('d');
                  return {cls: svg.getAttribute('class'), width: svg.getBoundingClientRect().width,
                          peak: d.split('C')[1].trim().split(/\\s+/).map(Number)[4]};
                }""")
                self.assertIn('stream-about-rise', rise['cls'])
                self.assertEqual(rise['width'], page.evaluate('document.documentElement.clientWidth'))
                # Under About on desktop, and under the menu trigger on a phone.
                anchor = page.locator('.masthead__trigger' if width < 800 else '.masthead__places a[href="#about"]')
                box = anchor.bounding_box()
                self.assertAlmostEqual(rise['peak'], box['x'] + box['width'] / 2, delta=0.6)
                page.keyboard.press('Escape')
                page.wait_for_function("() => document.getElementById('about').hidden")
                self.assertEqual(urlsplit(page.url).fragment, '')
                self.assertEqual(page.evaluate("document.activeElement.getAttribute('href') === '#about' || document.activeElement.classList.contains('masthead__trigger')"), True)
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                self.assertEqual(page.errors, [])
                page.close()

    def test_open_in_place_reduced_motion_shows_the_final_state_at_once(self):
        page = self.open(self.context(reduced_motion='reduce'), self.GRID)
        page.locator('.stream-card [data-open="fields-on-the-map"]').click()
        # No animation runs, so the panel is at full height on the next frame.
        state = page.evaluate("""() => new Promise(resolve => requestAnimationFrame(() => {
          const panel = document.getElementById('stream-panel');
          resolve({animations: document.getAnimations().length, moving: panel.classList.contains('is-moving'),
                   height: panel.getBoundingClientRect().height});
        }))""")
        self.assertEqual(state['animations'], 0)
        self.assertFalse(state['moving'])
        self.assertGreater(state['height'], 400)
        page.keyboard.press('Escape')
        self.assertEqual(page.locator('.stream-panel').count(), 0)
        self.assertEqual(page.errors, [])

    def test_open_in_place_every_kind_fits_a_phone_without_sideways_scroll(self):
        page = self.open(self.context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True), self.GRID)
        kinds = ['expert-insights', 'fields-on-the-map', 'weekly-activity-calendar', 'channel-impact-simulator',
                 'description-generator', 'how-i-built-description-generator', 'filtering-fields',
                 'markdown-to-rich-text', 'family-week', 'plinth']
        for item_id in kinds:
            with self.subTest(item=item_id):
                self.open_item(page, item_id)
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), 390)
                # Close is a 44px target at the top of the panel on a phone.
                close = page.locator('#stream-panel .stream-panel__close--head').bounding_box()
                self.assertGreaterEqual(close['height'], 44)
        self.assertEqual(page.errors, [])

    def test_open_in_place_prototypes_on_a_phone_follow_their_platform(self):
        context = self.context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        page = self.open(context, self.GRID)
        # A web prototype is not offered live on a phone.
        self.open_item(page, 'channel-impact-simulator')
        self.assertIn('Runs on a larger screen', page.locator('#stream-panel .stream-proto__note').text_content())
        self.assertEqual(page.locator('#stream-panel iframe').count(), 0)
        page.keyboard.press('Escape')
        # A mobile prototype whose demo is missing opens inline and says so.
        self.open_item(page, 'activity-central')
        self.assertIn('not published yet', page.locator('#stream-panel .stream-proto__note').text_content())
        page.keyboard.press('Escape')
        page.close()
        # With its demo published, it goes full screen and the back gesture closes it.
        page = context.new_page()
        page.errors = []
        page.on('pageerror', lambda error: page.errors.append(str(error)))
        page.route('**/demos/activity-central/**', lambda route: route.fulfill(
            content_type='text/html', body='<title>Activity Central demo</title>Demo'))
        page.goto(f'{ORIGIN}/{self.GRID}')
        self.settle(page)
        link = page.locator('.stream-card [data-open="activity-central"]')
        link.click()
        dialog = page.locator('dialog.stream-fullscreen')
        dialog.wait_for(state='visible')
        # Its own history entry, so that going back closes it.
        self.assertEqual(page.evaluate('history.state.streamFullscreen'), 'activity-central')
        self.assertEqual(urlsplit(page.url).fragment, 'activity-central')
        self.assertTrue(page.locator('.stream-fullscreen__close').evaluate('el => el === document.activeElement'))
        self.assertGreaterEqual(page.locator('.stream-fullscreen__close').bounding_box()['height'], 44)
        self.assertEqual(dialog.bounding_box()['width'], 390)
        page.go_back()
        page.wait_for_function("() => !document.querySelector('dialog.stream-fullscreen')")
        self.assertEqual(urlsplit(page.url).path, f'/{self.GRID}')
        self.assertEqual(urlsplit(page.url).fragment, '')
        self.assertTrue(link.evaluate('el => el === document.activeElement'))
        # Close does the same.
        link.click()
        dialog.wait_for(state='visible')
        page.locator('.stream-fullscreen__close').click()
        page.wait_for_function("() => !document.querySelector('dialog.stream-fullscreen')")
        self.assertEqual(urlsplit(page.url).fragment, '')
        self.assertFalse(page.evaluate('Boolean(history.state && history.state.streamFullscreen)'))
        self.assertEqual(page.errors, [])

    def test_open_in_place_cards_stay_links_without_javascript(self):
        page = self.open(self.context(java_script_enabled=False), self.GRID)
        link = page.locator('.stream-card [data-open="fields-on-the-map"]')
        self.assertIsNone(link.get_attribute('aria-expanded'))
        link.click()
        page.wait_for_url(f'{ORIGIN}/work/conservis#fig-conservis-03')
        self.assertEqual(page.locator('.stream-panel').count(), 0)

    # ---- Open in place on the real pages (Phase 2B integration) ----

    def test_open_in_place_real_grid_deep_link_filters_and_show_more(self):
        page = self.open(self.context(), 'index.html')
        cards = '[data-stream] > article'
        ids = self.item_ids(page, cards)
        self.assertGreater(len(ids), 33)
        deep = ids[33]
        # A deep link past the first 30 reveals up to its card, then opens it.
        page = self.open(self.context(), f'index.html#{deep}')
        self.wait_for_panel(page, deep)
        self.assertFalse(page.locator(f'#{deep}').evaluate('el => el.hidden'))
        self.assertGreaterEqual(int(page.locator('[data-pager-shown]').text_content()), 34)
        state = self.panel_state(page)
        self.assertEqual(state['prev'], self.row_end(page, f'{cards}:not([hidden])', deep))
        self.assertEqual((state['left'], state['width']), (0, state['viewport']))
        # Filtering out the open card closes its panel and clears the address.
        kind = page.locator(f'#{deep}').get_attribute('data-type')
        other = next(v for v in page.eval_on_selector_all('[data-filter="type"] option', 'els => els.map(el => el.value)') if v and v != kind)
        page.select_option('[data-filter="type"]', other)
        page.wait_for_function("() => !document.querySelector('.stream-panel')")
        self.assertEqual(urlsplit(page.url).fragment, '')
        # A filter that keeps the card moves the panel under its new row.
        page.select_option('[data-filter="type"]', '')
        screen = page.eval_on_selector_all(f'{cards}[data-type="screen"]:not([hidden])', 'els => els.map(el => el.id)')[4]
        self.open_item(page, screen)
        page.select_option('[data-filter="type"]', 'screen')
        page.wait_for_function("""id => {
          const panel = document.getElementById('stream-panel');
          const card = document.getElementById(id);
          return panel && panel.previousElementSibling && !card.hidden &&
            Math.abs(panel.previousElementSibling.getBoundingClientRect().top - card.getBoundingClientRect().top) < 2;
        }""", arg=screen)
        self.settle(page)
        state = self.panel_state(page)
        self.assertEqual(state['opener'], screen)
        self.assertEqual(state['prev'], self.row_end(page, f'{cards}:not([hidden])', screen))
        self.assertAlmostEqual(state['peak'], state['openerCentre'], delta=0.6)
        # Show more with the panel open leaves it under the same row.
        page.select_option('[data-filter="type"]', '')
        page.wait_for_function('id => !document.getElementById(id).hidden', arg=screen)
        self.settle(page)
        before = self.panel_state(page)['prev']
        page.locator('[data-pager-more]').click()
        self.settle(page)
        self.assertEqual(self.panel_state(page)['prev'], before)
        self.assertEqual(page.errors, [])

    def test_open_in_place_real_case_page_more_from_and_figure_anchors(self):
        for width in (1440, 390):
            with self.subTest(width=width):
                page = self.open(self.context(viewport={'width': width, 'height': 900}), 'work/conservis')
                link = page.locator('.more-from [data-open]').nth(2)
                item_id = link.get_attribute('data-open')
                link.scroll_into_view_if_needed()
                link.click()
                self.wait_for_panel(page, item_id)
                state = self.panel_state(page)
                # Full bleed, though More from's grid sits in the page's right column.
                self.assertEqual((state['left'], state['width']), (0, state['viewport']))
                self.assertEqual(state['tone'], 'band')
                # On its own case page the band does not link to that page.
                self.assertEqual(page.locator('#stream-panel .stream-panel__cta').count(), 0)
                # A figure anchor followed meanwhile stays in the address.
                page.evaluate("location.hash = '#fig-conservis-04'")
                page.wait_for_function("() => location.hash === '#fig-conservis-04'")
                page.keyboard.press('Escape')
                page.wait_for_function("() => !document.querySelector('.stream-panel')")
                self.assertEqual(urlsplit(page.url).fragment, 'fig-conservis-04')
                self.assertEqual(page.errors, [])
                page.close()
                # A figure anchor on load lands on the figure and opens nothing.
                page = self.open(self.context(viewport={'width': width, 'height': 900}), 'work/conservis#fig-conservis-04')
                page.wait_for_load_state('load')
                self.settle(page)
                self.assertEqual(page.locator('.stream-panel').count(), 0)
                self.assertLess(abs(page.locator('#fig-conservis-04').evaluate('el => el.getBoundingClientRect().top')), 80)
                page.close()
                # An item's id on load opens it in More from.
                page = self.open(self.context(viewport={'width': width, 'height': 900}), 'work/conservis#filtering-fields')
                self.wait_for_panel(page, 'filtering-fields')
                self.assertTrue(page.locator('#stream-panel').evaluate("el => Boolean(el.closest('.more-from'))"))
                self.assertEqual(page.errors, [])
                page.close()

    def test_open_in_place_real_about_opens_from_the_phone_menu_on_every_page(self):
        pages = ['index.html', 'work/', 'writing/', 'work/conservis', 'writing/how-i-built-description-generator']
        context = self.context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        for path in pages:
            with self.subTest(path=path):
                page = self.open(context, path)
                page.locator('.masthead__trigger').click()
                page.locator('.masthead__places a[href="#about"]').click()
                page.wait_for_function("() => !document.getElementById('about').hidden")
                self.settle(page)
                self.assertEqual(page.evaluate('document.activeElement.id'), 'about-title')
                peak = page.locator('#about').evaluate(
                    "el => Number(el.previousElementSibling.querySelector('path').getAttribute('d').split('C')[1].trim().split(/\\s+/)[4])")
                box = page.locator('.masthead__trigger').bounding_box()
                self.assertAlmostEqual(peak, box['x'] + box['width'] / 2, delta=0.6)
                page.locator('#about .about__close').click()
                page.wait_for_function("() => document.getElementById('about').hidden")
                self.assertTrue(page.locator('.masthead__trigger').evaluate('el => el === document.activeElement'))
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), 390)
                self.assertEqual(page.errors, [])
                page.close()

    # ---- Early QA pass (Phase 4, 2026-09-25) ----

    def test_qa_card_names_keep_every_meta_word_apart(self):
        # The separating dot is aria-hidden, so the spaces around it must sit
        # outside it, or a card reads "PrototypeProductivity" or "Writing2026".
        words = """el => {
          const copy = el.cloneNode(true);
          copy.querySelectorAll('[aria-hidden="true"]').forEach(hidden => hidden.replaceWith(' '));
          return copy.textContent.trim().split(/\\s+/);
        }"""
        spoken = """el => {
          const copy = el.cloneNode(true);
          copy.querySelectorAll('[aria-hidden="true"]').forEach(hidden => hidden.remove());
          return copy.textContent.trim().split(/\\s+/);
        }"""
        context = self.context()
        for path, meta in [('index.html', '.stream-card__meta'), ('list/index.html', '.stream-row__kind'),
                           ('work/conservis', '.stream-card__meta')]:
            page = self.open(context, path)
            for element in page.locator(meta).all():
                with self.subTest(path=path, meta=element.evaluate('el => el.id || el.textContent.trim()')):
                    self.assertEqual(element.evaluate(spoken), element.evaluate(words))
            page.close()
        # And the name Chromium computes for a card link, from the title and the meta line.
        page = self.open(context, 'index.html')
        for card_id, name in [('activity-central', 'Activity Central Prototype Productivity'),
                              ('how-i-built-description-generator', 'How I built Description Generator Writing 2026'),
                              ('expert-insights', 'Expert Insights Case study 7 screens'),
                              ('fields-on-the-map', 'Fields on the map Screen from the Conservis case study')]:
            with self.subTest(card=card_id):
                snapshot = page.locator(f'#{card_id} .stream-card__link').aria_snapshot()
                self.assertEqual(re.match(r'- link "(.*)"', snapshot).group(1), name)
        self.assertEqual(page.errors, [])

    def test_qa_case_study_strips_take_keyboard_focus_in_every_browser(self):
        # Chrome and Firefox make a scroller a tab stop on their own, and
        # Safari only does it for one that can take focus.
        for width in [1440, 390]:
            page = self.open(self.context(viewport={'width': width, 'height': 900}), 'index.html#expert-insights')
            self.wait_for_panel(page, 'expert-insights')
            track = page.locator('#stream-panel [data-strip-track]')
            self.assertEqual(track.get_attribute('tabindex'), '0')
            page.locator('#stream-panel-title').focus()
            page.keyboard.press('Tab')
            self.assertTrue(track.evaluate('el => el === document.activeElement'))
            count = page.locator('#stream-panel [data-strip-count]')
            first = count.text_content()
            page.keyboard.press('ArrowRight')
            page.wait_for_function('([el, text]) => el.textContent !== text', arg=[count.element_handle(), first])
            self.assertTrue(track.evaluate('el => el === document.activeElement'))
            self.assertEqual(page.errors, [])
            page.close()

    def test_qa_more_from_badges_keep_the_red_marker_of_the_grid(self):
        # A case study turns --accent into the project colour, which on the
        # badge's ink hid the Try it ▶. More from matches the Grid instead.
        marker = "el => getComputedStyle(el, '::before').color"
        context = self.context()
        page = self.open(context, 'index.html')
        red = page.locator('#activity-central .stream-card__badge').evaluate(marker)
        self.assertEqual(red, 'rgb(250, 25, 0)')
        page.close()
        for path, card_id in [('work/conservis', 'conservis-dashboard'), ('work/campaign-sim', 'channel-impact-simulator')]:
            with self.subTest(path=path):
                page = self.open(context, path)
                self.assertEqual(page.locator(f'.more-from #{card_id} .stream-card__badge').evaluate(marker), red)
                # The case study's own markers keep the project colour.
                self.assertNotEqual(page.locator('.case-study').evaluate("el => getComputedStyle(el).getPropertyValue('--accent')"),
                                    page.locator('.more-from').evaluate("el => getComputedStyle(el).getPropertyValue('--accent')"))
                page.close()

    def test_qa_more_from_cards_keep_the_grid_card_spacing(self):
        # --card-gap lived on .stream-grid only, so More from's cards set
        # their title and meta line flush under the image.
        spacing = """el => {
          const media = el.querySelector('.stream-card__media').getBoundingClientRect();
          const title = el.querySelector('.stream-card__title').getBoundingClientRect();
          const meta = el.querySelector('.stream-card__meta').getBoundingClientRect();
          return [Math.round(title.top - media.bottom), Math.round(meta.top - title.bottom)];
        }"""
        for width in [1440, 390]:
            options = {'viewport': {'width': width, 'height': 900}}
            if width < 600:
                options.update(is_mobile=True, has_touch=True)
            context = self.context(**options)
            page = self.open(context, 'index.html')
            grid = page.locator('#direct-expense-planning').evaluate(spacing)
            self.assertGreater(min(grid), 0)
            page.close()
            for path in ['work/conservis', 'work/campaign-sim', 'work/everag', 'work/vidscrip']:
                with self.subTest(width=width, path=path):
                    page = self.open(context, path)
                    for card in page.locator('.more-from .stream-card').all():
                        self.assertEqual(card.evaluate(spacing), grid)
                    page.close()

    def test_qa_index_calls_to_action_keep_the_space_before_the_arrow_on_phones(self):
        # On phones the call to action is a 44px flex row, which dropped the
        # space in "Read the case study →". Its width now matches the desktop's.
        measure = """el => {
          const text = document.createRange();
          text.selectNodeContents(el.firstChild);
          return { width: el.getBoundingClientRect().width, height: el.getBoundingClientRect().height,
                   arrow: el.querySelector('span').getBoundingClientRect().left - text.getBoundingClientRect().left };
        }"""
        for path in ['work/', 'writing/']:
            with self.subTest(path=path):
                desk = self.open(self.context(), path)
                wide = desk.locator('.entry__cta').first.evaluate(measure)
                desk.close()
                phone = self.open(self.context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True), path)
                ctas = phone.locator('.entry__cta')
                for i in range(ctas.count()):
                    narrow = ctas.nth(i).evaluate(measure)
                    self.assertAlmostEqual(narrow['arrow'], wide['arrow'], delta=0.5)
                    self.assertGreaterEqual(narrow['height'], 44)
                phone.close()

    def test_qa_list_marks_its_first_image_as_the_high_priority_lcp(self):
        # The List's first image is its largest paint, where the Grid's is its
        # headline, so only the List asks for fetchpriority.
        lcp = """() => new Promise(resolve => {
          new PerformanceObserver(list => {
            const last = list.getEntries().at(-1);
            resolve(last.element && last.element.closest('article') && last.element.closest('article').id);
          }).observe({ type: 'largest-contentful-paint', buffered: true });
        })"""
        for width in [1440, 390]:
            page = self.open(self.context(viewport={'width': width, 'height': 900}), 'list/index.html')
            first = page.locator('.stream-row img').first
            self.assertEqual(first.get_attribute('loading'), 'eager')
            self.assertEqual(first.get_attribute('fetchpriority'), 'high')
            self.assertEqual(page.locator('img[fetchpriority="high"]').count(), 1)
            self.assertEqual(page.evaluate(lcp), page.locator('.stream-row').first.get_attribute('id'))
            page.close()
        page = self.open(self.context(), 'index.html')
        self.assertEqual(page.locator('.stream-card img[fetchpriority]').count(), 0)
        page.close()

if __name__ == '__main__':
    unittest.main(verbosity=2)
