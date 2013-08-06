import os
import yaml
import codecs
import locale
import itertools
import jinja2
import re
import shutil

# -----------------------------------------------------------------------------

app_dir         = os.path.dirname(os.path.abspath(__file__))
page_dir        = os.path.join(app_dir, 'pages')
template_dir    = os.path.join(app_dir, 'templates')
default_charset = 'utf-8'

# -----------------------------------------------------------------------------

def make_nav(fn, extension = '.md'):
    def add_term(container, term):
        term = term.strip()
        if not term:
            return
        if term.startswith('/'):
            url = term
            path = ''.join([os.path.join(page_dir, url[1:]), extension])
            name = 'No Name'
            with codecs.open(path, 'r', encoding = default_charset) as f:
                lines = iter(f.read().split(u'\n'))
                # Read lines until an empty line is encountered.
                meta = u'\n'.join(itertools.takewhile(unicode.strip, lines))
                name = yaml.safe_load(meta)['title']
        else:
            url = '#'
            name = term
        container.append(name)
        container.append(url)
    with codecs.open(fn, 'r', encoding = default_charset) as f:
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

def make_nav_page(data_fn = os.path.join(page_dir, 'navigation.md'),
    src_fn = os.path.join(template_dir, 'navigation.html'),
    dst_fn = os.path.join(template_dir, 'rendered_navigation.html')):
    with codecs.open(src_fn, 'r', encoding = default_charset) as f:
        template = jinja2.Template(f.read())
    rendered_navigation = template.render(nav = make_nav(data_fn))
    with codecs.open(dst_fn, 'w', encoding = default_charset) as f:
        f.write(rendered_navigation)
    os.remove(data_fn)

# -----------------------------------------------------------------------------

def convert_charset(src_fn, dst_fn,
    src_formats = [locale.getpreferredencoding(), 'ascii'],
    dst_format = default_charset):
    for src_format in src_formats:
        try:
            with codecs.open(src_fn, 'r', src_format) as src_f:
                with codecs.open(dst_fn, 'w', dst_format) as dst_f:
                    for line in src_f:
                        dst_f.write(line)
                    return True
        except UnicodeDecodeError:
            pass
    return False

def make_page_utf8(target_ext = '.txt'):
    def _walk(directory):
        for name in os.listdir(directory):
            full_name = os.path.join(directory, name)
            if os.path.isdir(full_name):
                _walk(full_name)
            elif name.endswith(target_ext):
                convert_charset(full_name, full_name[:-len(target_ext)]+'.md')
    _walk(page_dir)

# -----------------------------------------------------------------------------

def make_image( target_ext = '.md',
                image_dir  = os.path.join(app_dir, 'static', 'img', 'content'),
                image_root = '/static/img/content/'):
    def _process(fn, prefix):
        img_regex = re.compile(r'(!.*?\[.*?\].*?)\((.*?)\)', re.I)
        with codecs.open(fn, 'r+', encoding = default_charset) as f:
            content = f.read()
            parent_path = os.path.dirname(fn)
            for img in img_regex.finditer(content):
                src_name = img.group(2)
                dst_name = '_'.join([prefix, src_name])
                # copy image
                src_path = os.path.join(parent_path, src_name)
                dst_path = os.path.join(image_dir, dst_name)
                if os.path.exists(src_path):
                    shutil.copy(src_path, dst_path)
            # replace link
            dst_link = r'\1(%s%s_\2)' % (image_root, prefix)
            f.seek(0)
            f.write(img_regex.sub(dst_link, content))
            f.truncate()
    def _walk(directory, path_prefix=()):
        for name in os.listdir(directory):
            full_name = os.path.join(directory, name)
            if os.path.isdir(full_name):
                _walk(full_name, path_prefix + (name,))
            elif name.endswith(target_ext):
                prefix = '_'.join(path_prefix)
                _process(full_name, prefix)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    _walk(page_dir)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(page_dir):
        os.makedirs(page_dir)
    make_page_utf8()
    make_nav_page()
    make_image()

# -----------------------------------------------------------------------------
