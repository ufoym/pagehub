import os
import yaml
import codecs
import locale
import itertools
from jinja2 import Template

app_dir = os.path.dirname(os.path.abspath(__file__))
page_dir= os.path.join(app_dir, 'pages')
template_dir = os.path.join(app_dir, 'templates')
code = locale.getpreferredencoding()
extension = '.txt'

# -----------------------------------------------------------------------------

def make_nav(fn):
    def add_term(container, term):
        term = term.strip()
        if not term:
            return
        term = term.decode(code)
        if term.startswith('/'):
            url = term
            path = ''.join([os.path.join(page_dir, url[1:]), extension])
            name = 'No Name'
            with codecs.open(path, 'r', encoding = code) as f:
                lines = iter(f.read().split(u'\n'))
                # Read lines until an empty line is encountered.
                meta = u'\n'.join(itertools.takewhile(unicode.strip, lines))
                name = yaml.safe_load(meta)['title']
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

def make_nav_page(data_fn = os.path.join(page_dir, 'navigation'),
    src_fn = os.path.join(template_dir, 'navigation.html'),
    dst_fn = os.path.join(template_dir, 'rendered_navigation.html')):
    with open(src_fn, 'r') as f:
        template = Template(f.read())
    os.rename(data_fn + extension, data_fn)
    rendered_navigation = template.render(nav = make_nav(data_fn))
    os.rename(data_fn, data_fn + extension)
    with open(dst_fn, 'w') as f:
        f.write(rendered_navigation.encode('utf-8'))

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    make_nav_page()

# -----------------------------------------------------------------------------