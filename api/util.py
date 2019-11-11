import functools
import re
from typing import Iterable

def search(seq: Iterable[str], q: str = None) -> Iterable[str]:
    pattern = q_re(q or "")
    return filter(pred(pattern), seq)


def pred(pattern: str):
    return functools.partial(re.search, pattern, flags=re.I)


def q_re(q: str) -> str:
    return re.escape(q or "").replace(r"\*", ".*").replace(r"\?", ".?")
