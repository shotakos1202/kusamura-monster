"""Build index.html (playable game) and dist/test.html (test hooks) from src/.

Usage: python3 tools/build.py
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = lambda p: open(os.path.join(ROOT, 'src', p), encoding='utf-8').read()

DOC_HEAD = ('<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n')

# Test hook: exposes internal state as window.__t for Playwright tests.
EXPORT = ("window.__t={MAPS,WALK,mon,loadMap,update,draw,pressed,setKey,SP,ART,startFish,spawnDrop,reachSet,bgmFor,AU,openBox,"
          "get S(){return S},set S(v){S=v},get Q(){return Q},get mode(){return mode},set mode(v){mode=v},"
          "get B(){return B},set B(v){B=v},get menu(){return menu},set menu(v){menu=v},get CUR(){return CUR},"
          "get P(){return P},get MG(){return MG},get shop(){return shop},set shop(v){shop=v},get boxui(){return boxui}};})();")

def main():
    shell, game = src('shell.html'), src('game.js').rstrip()
    assert game.endswith('})();')
    # artifact.html: body fragment used for the claude.ai artifact (no doctype; host wraps it)
    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    open(os.path.join(ROOT, 'dist', 'artifact.html'), 'w', encoding='utf-8').write(shell + '<script>\n' + game + '\n</script>\n')
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(DOC_HEAD + shell + '<script>\n' + game + '\n</script>\n')
    test = game[:-5] + EXPORT
    open(os.path.join(ROOT, 'dist', 'test.html'), 'w', encoding='utf-8').write(DOC_HEAD + shell + '<script>\n' + test + '\n</script>\n')
    print('built index.html, dist/artifact.html, dist/test.html')

if __name__ == '__main__':
    main()
