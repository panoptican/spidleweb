"""Behavior regressions for the product-description triage fixes.

Run with Python Playwright and its installed Chromium headless shell:
  python3 tests/browser_regressions.py

Resources are fulfilled from the checkout at a test origin. No preview server,
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
PAGES = ['index.html', *[str(p.relative_to(ROOT)) for p in sorted((ROOT / 'work').glob('*.html'))]]
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
            if path == ROOT:
                path = path / 'index.html'
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

    def featured_state(self, page):
        return page.evaluate("""() => {
          const items = [...document.querySelectorAll('.featured__item')];
          const shown = items.filter(el => getComputedStyle(el).display !== 'none' && getComputedStyle(el).visibility === 'visible');
          return {shown: shown.map(el => el.dataset.name),
            count: document.querySelector('.featured__position').textContent,
            next: document.querySelector('.featured__next-name').textContent};
        }""")

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
        context = self.context()
        for fragment in ['#%', '#[', '#missing-section', '#%70rofile']:
            with self.subTest(fragment=fragment):
                page = self.open(context, f'index.html{fragment}')
                self.assertEqual(page.errors, [])
                self.assertEqual(page.locator('.archive__nav .is-active').count(), 1)
                if fragment == '#%70rofile':
                    self.assertEqual(page.locator('.archive__nav .is-active').get_attribute('href'), '#profile')
                self.scroll_reveals(page)
                page.close()
        context = self.context()
        context.add_init_script('delete window.IntersectionObserver')
        page = self.open(context, 'index.html#%')
        self.assert_visible(page, motionless=True)
        self.assertEqual(page.errors, [])

    def test_b03_initial_and_live_reduced_motion(self):
        context = self.context(reduced_motion='reduce')
        for path in PAGES:
            page = self.open(context, path)
            self.assert_visible(page, motionless=True)
            page.close()
        context = self.context(reduced_motion='no-preference')
        for path in ['index.html']:
            page = self.open(context, path)
            self.assertGreater(page.locator('.reveal:not(.is-in)').count(), 0)
            page.emulate_media(reduced_motion='reduce')
            self.assert_visible(page, motionless=True)
            page.locator('.reveal').last.evaluate('el => el.scrollIntoView()')
            self.assert_visible(page, motionless=True)
            page.emulate_media(reduced_motion='no-preference')
            self.assert_visible(page)
            self.assertEqual(page.errors, [])
            page.close()

    def test_b04_b05_native_section_jumps_and_active_navigation(self):
        for width, height in [(1440, 900), (1440, 400), (900, 650), (390, 844), (1440, 1800)]:
            context = self.context(viewport={'width': width, 'height': height})
            page = self.open(context)
            for section in ['work', 'sites', 'profile', 'contact', 'sites']:
                with self.subTest(viewport=(width, height), section=section):
                    page.locator(f'.archive__nav a[href="#{section}"]').click()
                    page.mouse.move(width - 5, height - 5)
                    self.settle(page)
                    self.assertEqual(page.locator('.archive__nav .is-active').count(), 1)
                    self.assertEqual(page.locator('.archive__nav .is-active').get_attribute('href'), f'#{section}')
                    bounds = page.evaluate('''id => {
                      const header = document.querySelector('.archive__header');
                      return {heading: document.querySelector(`#${id} h2`).getBoundingClientRect().top,
                        header: getComputedStyle(header).position === 'sticky' ? header.getBoundingClientRect().bottom : 0};
                    }''', section)
                    self.assertGreaterEqual(bounds['heading'], bounds['header'] - 1)
                    if (width, height, section) == (1440, 900, 'sites'):
                        page.wait_for_function("() => [...document.querySelectorAll('#sites .reveal')].every(el => getComputedStyle(el).opacity === '1')")
                        self.screenshot(page, 'b04-b05-sites-jump')
            self.assertEqual(page.errors, [])
            page.close()
        # The CSS fallback must also offset native links when the script fails.
        page = self.open(self.context(block_script=True))
        for section in ['work', 'sites', 'profile']:
            page.locator(f'a[href="#{section}"]').click()
            heading = page.locator(f'#{section} h2').bounding_box()
            header = page.locator('.archive__header').bounding_box()
            self.assertGreaterEqual(heading['y'], header['y'] + header['height'] - 1)

    def test_b05_manual_scroll_repeat_click_keyboard_history_and_resize(self):
        page = self.open(self.context())
        page.locator('a[href="#sites"]').click()
        page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
        self.settle(page)
        self.assertEqual(page.locator('.archive__nav .is-active').get_attribute('href'), '#contact')
        page.locator('a[href="#sites"]').click()
        self.settle(page)
        self.assertEqual(page.locator('.archive__nav .is-active').get_attribute('href'), '#sites')
        page.locator('a[href="#profile"]').focus()
        page.keyboard.press('Enter')
        page.wait_for_url('**/index.html#profile')
        self.settle(page)
        self.assertEqual(page.locator('.archive__nav .is-active').get_attribute('href'), '#profile')
        page.go_back()
        self.settle(page)
        self.assertEqual(page.locator('.archive__nav .is-active').get_attribute('href'), '#sites')
        page.set_viewport_size({'width': 390, 'height': 844})
        page.locator('a[href="#profile"]').click()
        self.settle(page)
        self.assertEqual(page.locator('.archive__nav .is-active').get_attribute('href'), '#profile')
        self.assertAlmostEqual(page.locator('#profile h2').bounding_box()['y'], 0, delta=1)
        for section in ['work', 'sites', 'profile']:
            page.evaluate('''id => {
              const y = document.getElementById(id).getBoundingClientRect().top + scrollY;
              window.scrollTo(0, y + 2);
            }''', section)
            self.settle(page)
            self.assertEqual(page.locator('.archive__nav .is-active').get_attribute('href'), f'#{section}')
        self.assertEqual(page.errors, [])

    def test_b06_short_home_panel_and_flowing_case_context(self):
        for width in [1440, 800]:
            context = self.context(viewport={'width': width, 'height': 400})
            page = self.open(context)
            panel = page.locator('.panel')
            panel.hover(position={'x': 100, 'y': 100})
            page.mouse.wheel(0, 1200)
            page.wait_for_timeout(120)
            bounds = page.evaluate("""() => ({
              panel: document.querySelector('.panel').getBoundingClientRect().bottom,
              footer: document.querySelector('.panel__footer').getBoundingClientRect().bottom
            })""")
            self.assertLessEqual(bounds['footer'], bounds['panel'] - 20)
            page.close()
            for path in PAGES[1:]:
                page = self.open(context, path)
                rail = page.locator('.case-context')
                self.assertEqual(rail.evaluate('el => getComputedStyle(el).position'), 'static')
                rail.locator('p').last.scroll_into_view_if_needed()
                self.assertTrue(rail.locator('p').last.is_visible())
                self.assertEqual(rail.evaluate('el => el.scrollHeight'), rail.evaluate('el => el.clientHeight'))
                page.close()

    def test_b07_mobile_top_index_link_returns_home_on_every_case(self):
        context = self.context(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
        for path in PAGES[1:]:
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
                page.wait_for_url('**/index.html')
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
            self.assertIn('© 2027 JASON SPIDLE', page.locator('.footer').inner_text())
            page.close()
        context = self.context(java_script_enabled=False)
        for path in PAGES:
            page = self.open(context, path)
            self.assertIn('© 2026 JASON SPIDLE', page.locator('.footer').inner_text())
            page.close()

    def test_b10_external_links_use_this_tab_and_preserve_back_navigation(self):
        context = self.context(reduced_motion='reduce')
        count = 0
        for path in PAGES:
            page = self.open(context, path)
            links = page.locator('a[href^="https://"]').evaluate_all('els => els.map(el => ({href: el.getAttribute("href"), url: el.href}))')
            for link_info in links:
                href = link_info['href']
                with self.subTest(path=path, href=href):
                    link = page.locator(f'a[href="{href}"]')
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
        self.assertGreaterEqual(count, 15)
        page = self.open(context)
        with context.expect_page() as opened:
            page.locator('.sites__row').first.click(modifiers=['ControlOrMeta'])
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
            self.assertEqual(link.get_attribute('href'), f'{destination}.html')
            link.focus()
            self.assertEqual(link.evaluate('el => getComputedStyle(el).outlineStyle'), 'solid')
            page.keyboard.press('Enter')
            page.wait_for_url(f'**/work/{destination}.html')
        self.assertEqual(set(visited), set(expected))
        self.assertTrue(page.url.endswith('/work/everag.html'))

    def test_case_context_sticks_only_when_it_fits_and_stops_before_endpaper(self):
        context = self.context(reduced_motion='reduce')
        for path in PAGES[1:]:
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
        for path in PAGES[1:]:
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
        for path in PAGES[1:]:
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
                        masthead_colors[Path(path).name] = after['color']
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

    # ---- Homepage variant E: Featured, mode switch, feed door ----

    FEATURED = [('Expert Insights', 'work/expert-insights.html', 'VIEW CASE STUDY'),
                ('Atomic Tools', 'https://tools.spidleweb.net', 'USE THE TOOLS'),
                ('Two by Four', 'https://twobyfour.spidleweb.net', 'PLAY THE GAME')]
    VIEWPORTS = [(1440, 900), (834, 1112), (390, 844), (320, 844), (1440, 400)]

    def test_featured_never_advances_on_its_own(self):
        page = self.open(self.context(reduced_motion='no-preference'))
        before = self.featured_state(page)
        self.assertEqual(before, {'shown': ['Expert Insights'], 'count': '01 / 03', 'next': 'Atomic Tools'})
        page.wait_for_timeout(6000)
        self.assertEqual(self.featured_state(page), before)
        self.assertEqual(page.errors, [])

    def test_featured_next_wraps_through_every_item_without_moving_the_page(self):
        page = self.open(self.context(reduced_motion='reduce'))
        button = page.locator('.featured__next')
        self.assertEqual(page.locator('.featured__count').get_attribute('aria-live'), 'polite')
        names = [name for name, _, _ in self.FEATURED]
        geometry = []
        for step in range(len(names) + 1):
            index = step % len(names)
            state = self.featured_state(page)
            self.assertEqual(state['shown'], [names[index]])
            self.assertEqual(state['count'], f'0{index + 1} / 03')
            self.assertEqual(state['next'], names[(index + 1) % len(names)])
            self.assertIn(names[index], page.locator('.featured__count').text_content())
            item = page.locator('.featured__item.is-current')
            self.assertEqual(item.locator('.featured__cta').get_attribute('href'), self.FEATURED[index][1])
            self.assertIn(self.FEATURED[index][2], item.locator('.featured__cta').inner_text())
            self.assertTrue(item.locator('.featured__cta').is_visible())
            # Hidden items leave the tab order and the accessibility tree.
            self.assertEqual(page.locator('.featured__cta:visible').count(), 1)
            geometry.append(page.evaluate("""() => {
              const top = selector => document.querySelector(selector).getBoundingClientRect().top;
              const media = document.querySelector('.featured__item.is-current .featured__media').getBoundingClientRect();
              return [top('#work'), top('.featured__pager'), media.top, media.height];
            }"""))
            button.click()
        self.assertEqual(len(set(map(tuple, geometry))), 1, geometry)
        self.assertEqual(geometry[0][3], 244)
        self.assertEqual(page.errors, [])

    def test_featured_next_works_from_the_keyboard_and_keeps_focus(self):
        page = self.open(self.context(reduced_motion='reduce'))
        page.locator('.featured__item.is-current .featured__cta').focus()
        page.keyboard.press('Tab')
        self.assertEqual(page.locator(':focus').get_attribute('class'), 'featured__next')
        for key, expected in [('Enter', 'Atomic Tools'), ('Space', 'Two by Four'), ('Enter', 'Expert Insights')]:
            page.keyboard.press(key)
            self.assertEqual(self.featured_state(page)['shown'], [expected])
            self.assertEqual(page.locator(':focus').get_attribute('class'), 'featured__next')
        self.assertEqual(page.evaluate('scrollY'), 0)

    def test_featured_first_item_works_without_javascript(self):
        for options in ({'java_script_enabled': False}, {'block_script': True}):
            page = self.open(self.context(**options))
            with self.subTest(options=options):
                self.assertEqual(page.locator('.featured__item:visible').count(), 1)
                first = page.locator('.featured__item').first
                self.assertTrue(first.locator('.featured__headline').is_visible())
                self.assertEqual(first.locator('.featured__headline').inner_text(), 'AI-powered dashboard for soccer scouts')
                cta = first.locator('.featured__cta')
                self.assertTrue(cta.is_visible())
                self.assertEqual(cta.get_attribute('href'), 'work/expert-insights.html')
                self.assertFalse(page.locator('.featured__pager').is_visible())
                self.assertFalse(page.locator('.featured__next').is_visible())
                image = first.locator('img')
                self.assertTrue(image.is_visible())
                self.assertEqual(image.bounding_box()['height'], 242)
            page.close()
        page = self.open(self.context(java_script_enabled=False))
        page.locator('.featured__item .featured__cta').first.click()
        page.wait_for_url('**/work/expert-insights.html')

    def test_featured_items_are_complete_and_external_links_use_the_subdomains(self):
        page = self.open(self.context(reduced_motion='reduce'))
        items = page.locator('.featured__item')
        self.assertEqual(items.count(), len(self.FEATURED))
        for index, (name, href, label) in enumerate(self.FEATURED):
            item = items.nth(index)
            self.assertEqual(item.get_attribute('data-name'), name)
            self.assertTrue(item.locator('.featured__type').text_content().strip())
            self.assertTrue(item.locator('.featured__headline').text_content().strip())
            self.assertEqual(item.locator('.featured__media').locator('img, video').count(), 1)
            cta = item.locator('.featured__cta')
            self.assertEqual(cta.get_attribute('href'), href)
            self.assertIn(cta.get_attribute('target'), [None, '_self'])
        external = page.locator('.featured__cta[href^="https://"]').evaluate_all('els => els.map(el => el.hostname)')
        self.assertEqual(external, ['tools.spidleweb.net', 'twobyfour.spidleweb.net'])
        # No year is shown unless one is known.
        self.assertEqual([text.strip() for text in page.locator('.featured__type').all_text_contents()],
                         ['Case study · 2025', 'Tools', 'Game'])

    def test_featured_images_decode_from_the_checkout(self):
        for strip_avif in (False, True):
            page = self.open(self.context(reduced_motion='reduce'))
            if strip_avif:
                page.locator('.featured source').evaluate_all('els => els.forEach(el => el.remove())')
                page.locator('.featured img').evaluate_all("els => els.forEach(el => { el.src = el.getAttribute('src'); })")
            sources = page.locator('.featured img').evaluate_all("""async images => {
              await Promise.all(images.map(image => image.decode()));
              return images.map(image => ({src: image.currentSrc, ok: image.complete && image.naturalWidth > 0}));
            }""")
            self.assertEqual(len(sources), 3)
            for source in sources:
                self.assertTrue(source['ok'], source)
                self.assertTrue(source['src'].startswith(f'{ORIGIN}/assets/'), source)
                self.assertTrue((ROOT / source['src'][len(ORIGIN) + 1:]).is_file(), source)
            self.assertEqual(sum('/assets/placeholder-' in source['src'] for source in sources), 2)
            page.close()

    def test_featured_headlines_never_strand_a_word_and_swap_without_motion_when_reduced(self):
        for width, height in self.VIEWPORTS:
            page = self.open(self.context(viewport={'width': width, 'height': height}, reduced_motion='reduce'))
            for index in range(len(self.FEATURED)):
                lines = page.locator('.featured__item.is-current .featured__headline').evaluate("""el => {
                  const text = el.firstChild; const lines = new Map();
                  for (const match of text.textContent.matchAll(/\\S+/g)) {
                    const range = document.createRange();
                    range.setStart(text, match.index); range.setEnd(text, match.index + match[0].length);
                    const top = Math.round(range.getBoundingClientRect().top);
                    lines.set(top, (lines.get(top) || 0) + 1);
                  }
                  return [...lines.values()];
                }""")
                self.assertGreaterEqual(lines[-1], 2, ((width, height), index, lines))
                self.assertEqual(page.locator('.featured__item.is-current').evaluate(
                    'el => getComputedStyle(el).transitionDuration'), '0s')
                page.locator('.featured__next').click()
            self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'), width)
            page.close()
        page = self.open(self.context(reduced_motion='no-preference'))
        self.assertNotEqual(page.locator('.featured__item.is-current').evaluate(
            'el => getComputedStyle(el).transitionDuration'), '0s')

    def test_work_list_still_lists_all_six_projects(self):
        page = self.open(self.context(reduced_motion='reduce'))
        self.assertEqual(page.locator('.index__row').evaluate_all('els => els.map(el => el.getAttribute("href"))'),
                         [f'work/{slug}.html' for slug in ['expert-insights', 'campaign-sim', 'everag', 'vidscrip', 'conservis', 'plinth']])
        self.assertEqual(page.locator('.archive__nav a').first.inner_text(), 'WORK')
        self.assertEqual(page.locator('#work-title span').first.inner_text(), 'WORK')
        # Featured has no nav link, so it stays out of the scroll-spy's sections.
        self.assertEqual(page.locator('.archive__nav .is-active').get_attribute('href'), '#work')
        thumb = page.locator('.index__thumb').first.bounding_box()
        self.assertEqual((thumb['width'], thumb['height']), (72, 45))

    def test_mode_switch_marks_the_current_view_from_the_leading_side(self):
        for width, height in [(1440, 900), (390, 844)]:
            page = self.open(self.context(viewport={'width': width, 'height': height}))
            switch = page.locator('nav.mode-switch')
            self.assertEqual(switch.get_attribute('aria-label'), 'View')
            self.assertIsNone(switch.get_attribute('role'))
            links = switch.locator('a.mode-switch__link')
            self.assertEqual(links.evaluate_all('els => els.map(el => [el.textContent, el.getAttribute("href"), el.getAttribute("aria-current")])'),
                             [['Portfolio', 'index.html', 'page'], ['Feed', 'feed/', None]])
            marks = links.evaluate_all("""els => els.map(el => ['::before', '::after'].map(pseudo => {
              const style = getComputedStyle(el, pseudo);
              return style.content === 'none' ? null : [style.width, style.backgroundColor];
            }))""")
            self.assertEqual(marks, [[['6px', 'rgb(250, 25, 0)'], None], [None, None]])
            boxes = [link.bounding_box() for link in links.all()]
            for box in boxes:
                self.assertGreaterEqual(box['width'], 44)
                self.assertGreaterEqual(box['height'], 44)
            # The labels keep their order and their hit areas do not overlap.
            self.assertLessEqual(boxes[0]['x'] + boxes[0]['width'], boxes[1]['x'])
            # The padded hit areas leave the switch one text line tall.
            self.assertAlmostEqual(switch.bounding_box()['height'], links.first.evaluate(
                'el => parseFloat(getComputedStyle(el).lineHeight)'), delta=0.5)
            page.close()

    def test_feed_door_is_one_decorated_link_that_clears_the_seam(self):
        for width, height in self.VIEWPORTS:
            page = self.open(self.context(viewport={'width': width, 'height': height}, reduced_motion='reduce'))
            door = page.locator('a.feed-door')
            self.assertEqual(door.count(), 1)
            # The href is asserted, not followed: feed/ arrives with the Feed page.
            self.assertEqual(door.get_attribute('href'), 'feed/')
            self.assertEqual(page.locator('a[href="feed/"]').count(), 2)
            self.assertIn('FEED', door.inner_text())
            self.assertEqual(door.locator('img').evaluate_all('els => els.map(el => el.getAttribute("alt"))'), [''] * 5)
            page.locator('.panel').evaluate('el => { el.scrollTop = el.scrollHeight; }')
            clearance = page.evaluate("""() => {
              const panel = document.querySelector('.panel').getBoundingClientRect();
              const door = document.querySelector('.feed-door').getBoundingClientRect();
              const about = document.querySelector('.panel__about').getBoundingClientRect();
              const right = door.right - panel.left, bottom = door.bottom - panel.top;
              // Desktop seam: (100%, 4%) to (93.5%, 100%). Phone seam: (0, 100%) to (100%, 93%).
              const split = getComputedStyle(document.querySelector('.panel')).position === 'sticky';
              const seamX = panel.width * (1 - 0.065 * (bottom - 0.04 * panel.height) / (0.96 * panel.height));
              const seamY = panel.height * (1 - 0.07 * right / panel.width);
              return {gap: split ? seamX - right : seamY - bottom, inside: door.left >= panel.left && door.bottom <= panel.bottom,
                bottoms: Math.abs(door.bottom - about.bottom), beside: door.left >= about.right, split};
            }""")
            with self.subTest(viewport=(width, height)):
                self.assertGreaterEqual(clearance['gap'], 16, clearance)
                self.assertTrue(clearance['inside'], clearance)
                thumbs = door.locator('.feed-door__thumbs')
                if (width, height) == (1440, 900):
                    self.assertLess(clearance['bottoms'], 1, clearance)
                    self.assertTrue(clearance['beside'], clearance)
                    box = thumbs.bounding_box()
                    self.assertEqual((box['width'], box['height']), (188, 76))
                    sizes = thumbs.locator('img').evaluate_all('els => els.map(el => [el.offsetWidth, el.offsetHeight])')
                    self.assertEqual(sizes, [[60, 76], [60, 34], [60, 38], [60, 48], [60, 24]])
                    self.assertTrue(thumbs.locator('img').evaluate_all("""async images => {
                      images.forEach(image => { image.loading = 'eager'; });
                      await Promise.all(images.map(image => image.decode()));
                      return images.every(image => image.naturalWidth > 0);
                    }"""))
                # The thumbnails fold away on phones and short panels; the link itself never does.
                self.assertEqual(thumbs.is_visible(), width > 768 and height > 560)
                self.assertTrue(door.is_visible())
            page.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
