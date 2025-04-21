import os
import csv
import re
from flask import Flask, render_template, request, redirect, url_for
from duckduckgo_search import DDGS
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from search_controller import SongDatabase

# figure out the folder our code lives in
BASE_DIR       = os.path.dirname(__file__)
TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'templates')
STATIC_FOLDER   = os.path.join(BASE_DIR, 'static')
CSV_PATH       = os.path.join(BASE_DIR, 'lyrics.csv')

# initialize Flask with explicit template/static paths
app = Flask(
    __name__,
    template_folder=TEMPLATE_FOLDER,
    static_folder=STATIC_FOLDER
)

# load songs from CSV once
song_db = SongDatabase(CSV_PATH)

def make_snippet(text: str, term: str, window: int = 50) -> str:
    lo, hi = text.lower(), term.lower()
    idx = lo.find(hi)
    if idx == -1:
        s = text[:window]
        return s + ('…' if len(text) > window else '')
    start = max(0, idx - window)
    end   = min(len(text), idx + len(term) + window)
    snippet = text[start:end].replace('\n', ' ')
    return ('…' if start>0 else '') + snippet + ('…' if end<len(text) else '')

@app.route('/')
def home():
    return redirect(url_for('search'))

@app.route('/search')
def search():
    q      = request.args.get('q','').strip()
    source = request.args.get('source','web')
    results = []

    if q and source == 'web':
        with DDGS() as ddgs:
            ddg_results = ddgs.text(q, max_results=10)
        for item in ddg_results or []:
            results.append({
                'title':   item.get('title',''),
                'snippet': item.get('body',''),
                'url':     item.get('href','')
            })

    if q and source == 'local':
        pattern = re.compile(re.escape(q), re.IGNORECASE)
        for s in song_db.query_songs_by_filter(q):
            snippet = make_snippet(s.lyrics, q)
            results.append({
                'title':   s.song,
                'meta':    f"{s.year} • {s.artist}",
                'snippet': snippet,
                'id':      s.id
            })

    return render_template('search.html', q=q, source=source, results=results)

@app.route('/doc/<int:id>')
def doc(id):
    s = song_db.find_by_id(id)
    if not s:
        return "Not found", 404
    return render_template('document.html', doc={
        'title':  s.song,
        'artist': s.artist,
        'year':   s.year,
        'lyrics': s.lyrics,
        'rank':   s.id        # your template expects a rank field
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)