# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_flatpages import FlatPages
from flask_frozen import Freezer
import re, os, shutil

# -----------------------------------------------------------------------------

app = Flask(__name__)
app.config.from_pyfile('settings.py')
pages = FlatPages(app)
freezer = Freezer(app)
app_dir = os.path.dirname(os.path.abspath(__file__))
page_dir= os.path.join(app_dir, pages.config('root'))
img_dir = os.path.join(app_dir, 'static', 'img')

# -----------------------------------------------------------------------------

@app.route('/')
def home():
    posts = [page for page in pages if 'date' in page.meta]
    sorted_posts = sorted(posts, reverse=True,
        key=lambda page: page.meta['date'])
    nav = make_nav()
    return render_template('index.html', pages=sorted_posts, nav=nav)

@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    # copy images
    img_reg = re.compile(r'(<img .*?src=)"(.*?)"', re.I)
    org_dir = os.path.join(page_dir, *page.path.split('/')[:-1])
    for img in img_reg.finditer(page.html):
        img_fn = img.group(2)
        org_fn = os.path.join(org_dir, img_fn)
        new_fn = os.path.join(img_dir,
            '%s_%s' % (page.path.replace('/', '_'), img_fn))
        if os.path.exists(org_fn) and not os.path.exists(new_fn):
            shutil.copy(org_fn, new_fn)
    # update html
    img_rep = r'\1"/static/img/%s_\2"' % page.path.replace('/', '_')
    page.html = img_reg.sub(img_rep, page.html)
    nav = make_nav()
    return render_template('page.html', page=page, nav=nav)

# -----------------------------------------------------------------------------

def make_nav(fn = os.path.join(page_dir, 'cn.nav')):
    def add_term(container, term):
        term = term.strip()
        if not term:
            return
        term = unicode(term, 'utf-8')
        if term.startswith('/'):
            url = term
            name = pages.get(url[1:]).meta['title']
        else:
            url = '#'
            name = term
        container.append(name)
        container.append(url)
    with open(fn, 'r') as f:
        all_levels = []
        for line in f.readlines():
            single_level = []
            raw_terms = line.split(':')
            add_term(single_level, raw_terms[0])
            if len(raw_terms) > 1:
                for level1_term in raw_terms[1].split(','):
                    add_term(single_level, level1_term)
            all_levels.append(single_level)
    # structure:
    #    [[level0_name, level0_url, level1_name, level1_url, ...], [...], ...]
    return all_levels


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    using_dirs = [page_dir, img_dir]
    for using_dir in using_dirs:
        if not os.path.exists(using_dir):
            os.makedirs(using_dir)
    app.run()

# -----------------------------------------------------------------------------