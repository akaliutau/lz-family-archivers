import collections
import math
from typing import Any, TypeVar


class EntropyRecorder:
    _T = TypeVar('_T')  # Declare type variable

    def __init__(self):
        self.stat = collections.Counter()
        self.length = 0

    def add_sample(self, s: _T) -> _T:
        self.stat.update(collections.Counter(s))
        self.length += len(s)
        return s

    def entropy_shannon(self) -> float:
        # calculate probability for each byte as number of occurrences / array length
        probabilities = [n_x / self.length for x, n_x in self.stat.items()]

        # calculate per-character entropy fractions
        e_x = [-p_x * math.log(p_x, 2) for p_x in probabilities]

        # sum fractions to obtain Shannon entropy
        return sum(e_x)




