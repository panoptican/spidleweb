"""Behavior regressions for the product-description triage fixes.

Run with Python Playwright and its installed Chromium headless shell:
  python3 tests/browser_regressions.py

Resources are fulfilled from the checkout at a test origin. Clean URLs such as
/work/everag resolve to work/everag.html, as on Cloudflare Pages. No preview server,
external service, installed Chrome profile, or system-clock change is needed.
Set PLAYWRIGHT_CHROMIUM_EXECUTABLE to use another bundled Chromium binary.
"""
import mimetypes
import os
from pathlib import Path
import time
import unittest
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(os.environ.get('SPIDLEWEB_TEST_ROOT', Path(__file__).resolve().parents[1]))
ORIGIN = 'https://portfolio.test'
CASE_PAGES = [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'work').glob('*.html'))]
PAGES = ['index.html', 'feed/index.html', *CASE_PAGES]
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
            if block_script and url.path in ['/script.js', '/feed/feed.js']:
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

    def show_featured_link(self, page, link):
        """Page Featured forward until the item holding this link is the current one."""
        for _ in range(page.locator('.featured__item').count()):
            if link.is_visible():
                return
            page.locator('.featured__next').click()

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
                    if path == 'feed/index.html':
                        self.assertEqual(page.locator('h1').count(), 1)
                        self.assertTrue(page.locator('[data-feed-card]').first.is_visible())
                    else:
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

    def test_b07_mobile_top_index_link_returns_home_on_every_case(self):
        context = self.context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        for path in CASE_PAGES:
            with self.subTest(path=path):
                page = self.open(context, path)
                link = page.locator('.case-masthead__index')
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
              .filter(el => el.getClientRects().length || el.closest('.featured__item'))
              .map(el => [el.getAttribute("href"), {href: el.getAttribute("href"), url: el.href}])).values()]''')
            for link_info in links:
                href = link_info['href']
                with self.subTest(path=path, href=href):
                    link = page.locator(f'a[href="{href}"]:not(.about a)').first
                    self.assertIn(link.get_attribute('target'), [None, '_self'])
                    self.show_featured_link(page, link)
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

    def test_feed_monolith_layout_titles_icons_and_type_mix(self):
        page = self.open(self.context(viewport={'width': 1440, 'height': 900}), 'feed/')
        cards = page.locator('[data-feed-card]')
        self.assertEqual(cards.count(), 20)
        self.assertEqual(cards.evaluate_all("els => els.reduce((counts, el) => { counts[el.dataset.type] = (counts[el.dataset.type] || 0) + 1; return counts; }, {})"),
                         {'screens': 13, 'prototypes': 3, 'posts': 1, 'websites': 2, 'tools': 1})
        self.assertEqual(page.locator('.feed-stream').evaluate('el => getComputedStyle(el).columnCount'), '3')
        self.assertTrue(cards.evaluate_all("""els => els.every(card => {
          const footer = card.querySelector('.feed-card__footer').getBoundingClientRect();
          const title = card.querySelector('h2').getBoundingClientRect();
          const icons = card.querySelectorAll('.feed-card__type-icon img');
          const link = card.querySelector('[data-feed-action]');
          return card.id && link.dataset.feedAction === 'viewer' && link.hash === `#${card.id}` &&
            card.querySelector('h2').textContent.trim().length > 8 &&
            title.width <= footer.width * 0.62 && icons.length === 2;
        })"""))
        self.assertTrue(page.locator('.feed-card__media img').evaluate_all("""async images => {
          await Promise.all(images.map(image => image.decode()));
          return images.every(image => {
            const declaredRatio = Number(image.getAttribute('width')) / Number(image.getAttribute('height'));
            const loadedRatio = image.naturalWidth / image.naturalHeight;
            return image.complete && image.naturalWidth > 0 && Math.abs(declaredRatio - loadedRatio) < 0.01 &&
              image.alt.trim() && image.currentSrc.endsWith('.avif');
          });
        }"""))
        self.assertEqual(page.locator('.feed-card__media picture source[type="image/avif"]').count(), 20)
        self.assertTrue(page.locator('.feed-card__media picture source').evaluate_all(
            "els => els.every(el => el.srcset.includes(' 480w') && el.sizes.trim())"))
        self.assertEqual(page.locator('[data-status="placeholder"]').count(), 7)
        self.assertEqual(page.errors, [])

    def test_feed_hover_reveals_color_lift_and_red_icon_with_reduced_motion_fallback(self):
        page = self.open(self.context(), 'feed/')
        link = page.locator('[data-dialog-link="scouting-sentiment-search"]')
        before = link.evaluate("""el => ({
          slab: getComputedStyle(el, '::before').backgroundColor,
          slabTransform: getComputedStyle(el, '::before').transform,
          surface: getComputedStyle(el.querySelector('.feed-card__surface')).transform,
          black: getComputedStyle(el.querySelector('.feed-card__type-icon img:first-child')).opacity,
          red: getComputedStyle(el.querySelector('.feed-card__type-icon img:last-child')).opacity
        })""")
        link.hover()
        page.wait_for_timeout(180)
        after = link.evaluate("""el => ({
          slab: getComputedStyle(el, '::before').backgroundColor,
          slabTransform: getComputedStyle(el, '::before').transform,
          surface: getComputedStyle(el.querySelector('.feed-card__surface')).transform,
          black: getComputedStyle(el.querySelector('.feed-card__type-icon img:first-child')).opacity,
          red: getComputedStyle(el.querySelector('.feed-card__type-icon img:last-child')).opacity
        })""")
        self.assertEqual(before['slab'], 'rgb(10, 10, 10)')
        self.assertNotEqual(after['slab'], before['slab'])
        self.assertNotEqual(after['slabTransform'], before['slabTransform'])
        self.assertNotEqual(after['surface'], before['surface'])
        self.assertEqual((before['black'], before['red']), ('1', '0'))
        self.assertEqual((after['black'], after['red']), ('0', '1'))
        page.close()

        page = self.open(self.context(reduced_motion='reduce'), 'feed/')
        self.assertTrue(page.locator('.feed-card__surface, .feed-card__type-icon img').evaluate_all(
            "els => els.every(el => getComputedStyle(el).transitionDuration.split(',').every(value => parseFloat(value) === 0))"))

    def test_feed_filters_keep_twenty_item_source_and_follow_browser_history(self):
        page = self.open(self.context(reduced_motion='reduce'), 'feed/')
        self.assertTrue(page.locator('[data-feed-filters]').is_visible())
        self.assertEqual(page.locator('[data-feed-card]:not([hidden])').count(), 20)
        type_filter = page.locator('[data-filter="type"]')
        type_filter.locator('summary').click()
        type_filter.locator('[data-filter-value="prototypes"]').click()
        self.assertEqual(page.locator('[data-feed-card]:not([hidden])').count(), 3)
        industry_filter = page.locator('[data-filter="industry"]')
        industry_filter.locator('summary').click()
        industry_filter.locator('[data-filter-value="sports"]').click()
        self.assertEqual(page.locator('[data-feed-card]:not([hidden])').count(), 2)
        self.assertEqual(dict(item.split('=') for item in urlsplit(page.url).query.split('&')),
                         {'type': 'prototypes', 'industry': 'sports'})
        page.go_back()
        self.settle(page)
        self.assertEqual(page.locator('[data-feed-card]:not([hidden])').count(), 3)
        self.assertEqual(page.locator('[data-filter="industry"] [data-filter-label]').text_content(), 'All')
        page.go_back()
        self.settle(page)
        self.assertEqual(page.locator('[data-feed-card]:not([hidden])').count(), 20)
        page.go_forward()
        self.settle(page)
        self.assertEqual(page.locator('[data-feed-card]:not([hidden])').count(), 3)
        page.go_forward()
        self.settle(page)
        self.assertEqual(page.locator('[data-feed-card]:not([hidden])').count(), 2)
        page.reload()
        page.evaluate('document.fonts.ready')
        self.settle(page)
        self.assertEqual(page.locator('[data-feed-card]:not([hidden])').count(), 2)
        self.assertEqual(page.locator('[data-filter="type"] [data-filter-label]').text_content(), 'Prototypes')

    def test_feed_restores_scroll_after_leaving_and_returning(self):
        page = self.open(self.context(reduced_motion='reduce'), 'feed/')
        return_link = page.locator('.feed-endpaper__link')
        return_link.evaluate("el => el.scrollIntoView({block: 'center'})")
        expected = page.evaluate('scrollY')
        self.assertGreater(expected, 300)
        return_link.click()
        page.wait_for_url(f'{ORIGIN}/index.html#work')
        page.go_back()
        page.wait_for_url(f'{ORIGIN}/feed/')
        page.wait_for_function('expected => Math.abs(scrollY - expected) < 3', arg=expected)
        self.assertAlmostEqual(page.evaluate('scrollY'), expected, delta=2)
        self.assertEqual(page.errors, [])

    def test_feed_viewer_uses_item_galleries_deep_links_and_restores_focus(self):
        page = self.open(self.context(reduced_motion='reduce'), 'feed/')
        opener = page.locator('[data-dialog-link="scouting-sentiment-search"]')
        opener.focus()
        opener.click()
        dialog = page.locator('[data-feed-dialog]')
        self.assertTrue(dialog.evaluate('el => el.open'))
        self.assertTrue(page.locator('[data-feed-page]').evaluate('el => el.inert'))
        self.assertEqual(dialog.locator('[data-dialog-title]').inner_text(), 'Scouting sentiment search')
        self.assertTrue(page.url.endswith('#scouting-sentiment-search'))
        self.assertEqual(dialog.locator('[data-dialog-count]').inner_text(), '01 / 01')
        self.assertTrue(dialog.locator('[data-dialog-previous]').is_hidden())
        page.keyboard.press('ArrowRight')
        self.assertEqual(dialog.locator('[data-dialog-title]').inner_text(), 'Scouting sentiment search')
        self.assertTrue(page.url.endswith('#scouting-sentiment-search'))
        page.keyboard.press('Escape')
        self.assertFalse(dialog.evaluate('el => el.open'))
        self.assertFalse(page.locator('[data-feed-page]').evaluate('el => el.inert'))
        self.assertEqual(page.evaluate('document.activeElement.dataset.dialogLink'), 'scouting-sentiment-search')
        self.assertEqual(urlsplit(page.url).fragment, '')

        gallery_opener = page.locator('[data-dialog-link="channel-impact-simulator"]')
        gallery_opener.focus()
        gallery_opener.click()
        first_alt = dialog.locator('[data-dialog-media] img').get_attribute('alt')
        self.assertEqual(dialog.locator('[data-dialog-count]').inner_text(), '01 / 04')
        self.assertTrue(dialog.locator('[data-dialog-next]').is_visible())
        page.keyboard.press('ArrowRight')
        self.assertEqual(dialog.locator('[data-dialog-count]').inner_text(), '02 / 04')
        self.assertNotEqual(dialog.locator('[data-dialog-media] img').get_attribute('alt'), first_alt)
        self.assertTrue(page.url.endswith('#channel-impact-simulator'))
        page.keyboard.press('Shift+Tab')
        self.assertTrue(page.evaluate('document.activeElement.hasAttribute("data-dialog-next")'))
        page.keyboard.press('Tab')
        self.assertTrue(page.evaluate('document.activeElement.hasAttribute("data-dialog-close")'))
        page.keyboard.press('Escape')
        self.assertEqual(page.evaluate('document.activeElement.dataset.dialogLink'), 'channel-impact-simulator')

        page.goto(f'{ORIGIN}/feed/#field-task-setup')
        page.evaluate('document.fonts.ready')
        self.settle(page)
        self.assertTrue(dialog.evaluate('el => el.open'))
        self.assertEqual(dialog.locator('[data-dialog-title]').inner_text(), 'Field task setup')
        self.assertEqual(dialog.get_attribute('data-orientation'), 'standard')
        self.assertEqual(page.errors, [])

    def test_feed_without_javascript_keeps_all_items_and_hash_fallbacks_reachable(self):
        page = self.open(self.context(java_script_enabled=False), 'feed/')
        self.assertFalse(page.locator('[data-feed-filters]').is_visible())
        cards = page.locator('[data-feed-card]')
        self.assertEqual(cards.count(), 20)
        self.assertTrue(cards.evaluate_all("els => els.every(el => !el.hidden && el.getBoundingClientRect().height > 0)"))
        self.assertTrue(cards.locator('a[data-feed-action="viewer"]').evaluate_all(
            "els => els.every(el => el.hash === `#${el.closest('[data-feed-card]').id}`)"))
        page.locator('[data-dialog-link="field-task-setup"]').click()
        self.assertEqual(urlsplit(page.url).fragment, 'field-task-setup')
        target = page.locator('#field-task-setup')
        self.assertEqual(target.evaluate('el => getComputedStyle(el).position'), 'fixed')
        self.assertTrue(target.locator('.feed-card__media img').is_visible())
        self.assertTrue(page.locator('.feed-fallback-close').is_visible())
        page.locator('.feed-fallback-close').click()
        self.assertEqual(urlsplit(page.url).fragment, 'feed-stream')
        self.assertEqual(page.errors, [])

    def test_feed_has_no_horizontal_overflow_at_all_review_sizes(self):
        for width, height in [(1440, 900), (834, 1112), (390, 844), (320, 844), (1440, 400)]:
            with self.subTest(viewport=(width, height)):
                page = self.open(self.context(viewport={'width': width, 'height': height}), 'feed/')
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                page.goto(f'{ORIGIN}/feed/#channel-impact-simulator')
                self.settle(page)
                self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
                self.assertEqual(page.errors, [])
                page.close()

    def test_case_endpapers_match_destinations_and_complete_the_cycle(self):
        expected = {'everag': 'vidscrip', 'vidscrip': 'conservis', 'conservis': 'plinth',
                    'plinth': 'expert-insights', 'expert-insights': 'campaign-sim', 'campaign-sim': 'everag'}
        context = self.context(reduced_motion='reduce')
        themes = {}
        for slug in expected:
            page = self.open(context, f'work/{slug}.html')
            themes[slug] = page.evaluate("""() => ({
              bg: getComputedStyle(document.querySelector('.case-masthead'), '::before').backgroundColor,
              fg: getComputedStyle(document.querySelector('.case-masthead')).color,
              paper: getComputedStyle(document.body).backgroundColor
            })""")
            page.close()
        page = self.open(context, 'work/everag.html')
        visited = []
        for _ in expected:
            slug = Path(urlsplit(page.url).path).stem
            visited.append(slug)
            destination = expected[slug]
            actual = page.evaluate("""() => ({
              bg: getComputedStyle(document.querySelector('.case-endpaper'), '::before').backgroundColor,
              fg: getComputedStyle(document.querySelector('.case-endpaper')).color,
              paper: getComputedStyle(document.body).backgroundColor
            })""")
            self.assertEqual(actual['bg'], themes[destination]['bg'])
            self.assertEqual(actual['fg'], themes[destination]['fg'])
            self.assertEqual(actual['paper'], themes[slug]['paper'])
            self.assertNotEqual(actual['bg'], themes[slug]['bg'])
            link = page.locator('.case-endpaper__next')
            self.assertEqual(link.get_attribute('href'), f'/work/{destination}')
            link.focus()
            self.assertEqual(link.evaluate('el => getComputedStyle(el).outlineStyle'), 'solid')
            page.keyboard.press('Enter')
            page.wait_for_url(f'{ORIGIN}/work/{destination}')
        self.assertEqual(set(visited), set(expected))
        self.assertEqual(page.url, f'{ORIGIN}/work/everag')

    def test_case_context_sticks_only_when_it_fits_and_stops_before_endpaper(self):
        context = self.context(reduced_motion='reduce')
        for path in CASE_PAGES:
            page = self.open(context, path)
            rail = page.locator('.case-context')
            self.assertEqual(rail.evaluate('el => getComputedStyle(el).position'), 'sticky')
            page.evaluate('scrollTo(0, 1000)')
            self.settle(page)
            self.assertAlmostEqual(rail.bounding_box()['y'], 24, delta=1)
            page.locator('.case-endpaper').scroll_into_view_if_needed()
            self.settle(page)
            bounds = rail.bounding_box()
            end = page.locator('.case-endpaper').bounding_box()
            self.assertLessEqual(bounds['y'] + bounds['height'], end['y'])
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
            self.assertEqual(page.locator(':focus').get_attribute('class'), 'case-masthead__identity')
            page.keyboard.press('Tab')
            self.assertEqual(page.locator(':focus').get_attribute('class'), 'case-masthead__index')
            self.assertEqual(page.locator('.case-proofs a[href*="assets/"]').count(), 0)
            self.assertEqual(page.locator('a:has(img)').count(), 0)
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
        masthead_colors = {}
        endpaper_colors = []
        for path in CASE_PAGES:
            page = self.open(context, path)
            for selector in ['.case-masthead a', '.case-context__links a', '.case-endpaper__nav a']:
                for link in page.locator(selector).all():
                    page.mouse.move(0, 0)
                    before = link.evaluate('el => ({color: getComputedStyle(el).color, bg: getComputedStyle(el).backgroundColor})')
                    link.hover()
                    after = link.evaluate('el => ({color: getComputedStyle(el).color, bg: getComputedStyle(el).backgroundColor, decoration: getComputedStyle(el).textDecorationLine})')
                    self.assertNotEqual(before['color'], after['color'])
                    self.assertNotEqual(after['color'], 'rgb(250, 25, 0)')
                    self.assertEqual(after['bg'], before['bg'])
                    self.assertEqual(after['decoration'], 'none')
                    if selector == '.case-masthead a':
                        masthead_colors[f'/work/{Path(path).stem}'] = after['color']
                    elif selector == '.case-endpaper__nav a':
                        destination = page.locator('.case-endpaper__next').get_attribute('href')
                        endpaper_colors.append((destination, after['color']))
            page.close()
        self.assertEqual(len(set(masthead_colors.values())), 6)
        for destination, color in endpaper_colors:
            self.assertEqual(color, masthead_colors[destination])
        page = self.open(self.context(reduced_motion='reduce'), 'work/expert-insights.html')
        for i in [5, 6, 7]:
            image = page.locator(f'img[src$="expert-insights-0{i}-full.png"]')
            self.assertEqual(image.count(), 1)
            self.assertEqual(image.get_attribute('width'), '2880')
            self.assertEqual(image.get_attribute('height'), '2048')


if __name__ == '__main__':
    unittest.main(verbosity=2)
