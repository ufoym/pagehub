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

    # process images in subfolder
    root = os.path.dirname(os.path.abspath(__file__))
    img_reg = re.compile(r'(<img .*?src=)"(.*?)"', re.I)
    img_rep = r'\1"/static/img/%s_\2"' % page.path.replace('/', '_')
    # copy images
    new_dir = os.path.join(root, 'static', 'img')
    org_dir = os.path.join(root, 'pages', *page.path.split('/')[:-1])
    for img in img_reg.finditer(page.html):
        img_fn = img.group(2)
        org_fn = os.path.join(org_dir, img_fn)
        new_fn = os.path.join(new_dir,
            '%s_%s' % (page.path.replace('/', '_'), img_fn))
        shutil.copy2(org_fn, new_fn)
    page.html = img_reg.sub(img_rep, page.html)
    return render_template('page.html', page=page)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run()

# -----------------------------------------------------------------------------