import csv, re
from typing import List, Optional

class Song:
    def __init__(self, id: int, song: str, artist: str, year: int, lyrics: str):
        self.id     = id
        self.song   = song
        self.artist = artist
        self.year   = year
        self.lyrics = lyrics

class SongDatabase:
    def __init__(self, csv_path: str):
        self.songs: List[Song] = []
        with open(csv_path, encoding='latin-1') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=1):
                # use the CSV’s actual column names here:
                self.songs.append(Song(
                    id=idx,
                    song=row['Song'],
                    artist=row['Artist'],
                    year=int(row['Year']),
                    lyrics=row['Lyrics']
                ))

    def query_songs_by_filter(self, filter_str: str) -> List[Song]:
        """Match against song title, artist, year, or lyrics (case‑insensitive)."""
        regex = re.compile(re.escape(filter_str), re.IGNORECASE)
        matches = []
        for s in self.songs:
            # search in song title, artist, lyrics, or stringified year
            if (regex.search(s.song)
             or regex.search(s.artist)
             or regex.search(s.lyrics)
             or regex.search(str(s.year))):
                matches.append(s)
        return matches

    def find_by_id(self, id: int) -> Optional[Song]:
        for s in self.songs:
            if s.id == id:
                return s
        return None

def make_snippet(text: str, term: str, window: int = 50) -> str:
    """Return a KWIC snippet of `text` around the first occurrence of `term`."""
    lo, hi = text.lower(), term.lower()
    idx = lo.find(hi)
    if idx == -1:
        return text[:window] + ("…" if len(text) > window else "")
    start = max(0, idx - window)
    end   = min(len(text), idx + len(term) + window)
    snippet = text[start:end].replace('\n', ' ')
    return ('…' if start > 0 else '') + snippet + ('…' if end < len(text) else '')
