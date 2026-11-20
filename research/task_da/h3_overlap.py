"""Offline fixed-snapshot policies. Never imported by the ANN search engine."""
import itertools


def metrics(sets, assignment):
    u = [set(), set()]
    for s, w in zip(sets, assignment, strict=True):
        u[w].update(s)
    return dict(max_work=max(map(len, u)), duplicate=len(u[0] & u[1]),
                total=sum(map(len, u)), imbalance=abs(len(u[0])-len(u[1])))


def assign(seeds, policy, signatures=None):
    """One seed/rank-pair/worker; deterministic RR ties and RR singleton tail."""
    n = len(seeds)
    rr = [i % 2 for i in range(n)]
    if policy == 'rr':
        return rr
    sets = [set(s['eligible']) for s in seeds]
    if policy in ('exact_quartet', 'signature', 'placebo'):
        a = rr[:]
        for i in range(0, n-3, 4):
            candidates = ([0, 1, 0, 1], [0, 1, 1, 0])
            def score(part):
                if policy == 'exact_quartet':
                    m = metrics(sets[i:i+4], part)
                    return m['max_work'], m['total']
                u = [0, 0]
                for j, w in enumerate(part):
                    u[w] |= signatures[i+j]
                c = list(map(int.bit_count, u))
                return max(c), sum(c)
            a[i:i+4] = min(enumerate(candidates), key=lambda x:(score(x[1]),x[0]))[1]
        return a
    a, u, load = [], [set(), set()], [0, 0]
    for i in range(0, n-1, 2):
        def score(part):
            if policy == 'exact_greedy':
                x = [u[w] | sets[i+part.index(w)] for w in range(2)]
                c = list(map(len, x))
                return max(c), sum(c)
            weight = [seeds[i+j]['degree'] if policy == 'degree' else len(sets[i+j]) for j in range(2)]
            c = [load[w] + weight[part.index(w)] for w in range(2)]
            return max(c), abs(c[0]-c[1])
        part = min(enumerate(([0,1], [1,0])),key=lambda x:(score(x[1]),x[0]))[1]
        a.extend(part)
        for j,w in enumerate(part):
            u[w].update(sets[i+j])
            load[w] += seeds[i+j]['degree'] if policy == 'degree' else len(sets[i+j])
    if n % 2:
        a.append(rr[-1])
    return a


def exact_oracle(seeds):
    """Exhaustive optimum over all balanced rank-pair orientations, <=32 seeds.

    Whole-round (max union, sum union) objective, fixed first pair by symmetry.
    Singleton tail remains RR, so symmetry reduction applies only for even n.
    """
    n = len(seeds)
    if n > 32:
        raise ValueError('oracle cap 32 seeds')
    sets = [set(s['eligible']) for s in seeds]
    ids = sorted(set().union(*sets)) if sets else []
    bits = {v:1 << i for i,v in enumerate(ids)}
    masks = [sum(bits[v] for v in s) for s in sets]
    pairs = n//2
    best = None
    for orientation in itertools.product((0,1),repeat=max(0,pairs-(1 if n%2 == 0 and pairs else 0))):
        orientations = ((0,)+orientation) if n%2 == 0 and pairs else orientation
        a = [w for flip in orientations for w in (flip,1-flip)]
        if n%2:a.append(0)
        u = [0,0]
        for mask,w in zip(masks,a):u[w] |= mask
        c = [x.bit_count() for x in u]
        score = (max(c),sum(c))
        if best is None or score < best[0]:best = (score,a)
    return best[1]
