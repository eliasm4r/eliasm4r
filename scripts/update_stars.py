"""Refresh the star count shown on each side-quest card from the GitHub API."""
import glob, json, math, os, re, sys, urllib.request

AMB = '#e3b341'
MARK = re.compile(r'<!--stars:([\w.-]+/[\w.-]+)-->.*?<!--/stars-->', re.S)


def render(repo, n):
    if n <= 0:
        return f'<!--stars:{repo}--><!--/stars-->'
    x, y, r = 344, 52, 8
    pts = ' '.join(f'{x + (r if k % 2 == 0 else r * .45) * math.sin(k * math.pi / 5):.1f},'
                   f'{y - (r if k % 2 == 0 else r * .45) * math.cos(k * math.pi / 5):.1f}' for k in range(10))
    return (f'<!--stars:{repo}--><polygon points="{pts}" fill="{AMB}"/>'
            f'<text x="358" y="57" font-size="14" font-weight="700" fill="{AMB}">{n}</text><!--/stars-->')


def stars(repo):
    req = urllib.request.Request(f'https://api.github.com/repos/{repo}',
                                 headers={'Accept': 'application/vnd.github+json'})
    if os.environ.get('GITHUB_TOKEN'):
        req.add_header('Authorization', f"Bearer {os.environ['GITHUB_TOKEN']}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)['stargazers_count']


def update(text, fetch):
    return MARK.sub(lambda m: render(m.group(1), fetch(m.group(1))), text)


if __name__ == '__main__':
    if '--test' in sys.argv:
        sample = 'a<!--stars:o/r-->old<!--/stars-->b'
        assert update(sample, lambda r: 0) == 'a<!--stars:o/r--><!--/stars-->b'
        out = update(sample, lambda r: 9)
        assert '>9</text>' in out and out.startswith('a<!--stars:o/r--><polygon') and out.endswith('<!--/stars-->b')
        assert update(update(sample, lambda r: 9), lambda r: 9) == out  # idempotent
        print('ok'); sys.exit()
    for path in glob.glob('assets/quest*.svg'):
        old = open(path, encoding='utf-8').read()
        new = update(old, stars)  # an API error stops the run, so no card is ever wiped
        if new != old:
            open(path, 'w', encoding='utf-8').write(new)
            print('updated', path)
