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
    return render_template('index.html', pages=sorted_posts)

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
            img_rep = r'/static/img/%s_%s"' \
                    % (page.path.replace('/', '_'), img_fn)
            page.html = page.html.replace(img_fn, img_rep)
    return render_template('page.html', page=page)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    using_dirs = [page_dir, img_dir]
    for using_dir in using_dirs:
        if not os.path.exists(using_dir):
            os.makedirs(using_dir)
    app.run()

# -----------------------------------------------------------------------------