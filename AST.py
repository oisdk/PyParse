from functools import reduce
class AST:

    def __init__(self, result, op=None, children=[]):
        self._res = result
        self._opr = op
        self._chd = children
        self._chr = op or ('T' if result == True else 'F' if result == False else str(result))

    def __repr__(self):
        return buchheim(self).svg

class DrawTree:

    def __init__(self, tree, parent=None, depth=0, number=1):
        self._loc = (-1., depth)
        self._tre = tree
        self._chd = [DrawTree(c, self, depth+1, i+1) for i, c in enumerate(tree._chd)]
        self._pnt = parent
        self._thd = None
        self._mod = 0
        self._anc = self
        self._chg = self._sft = 0
        self._lmost_sibling = None
        self._num = number

    def left(self):
        return self._thd or self._chd and self._chd[0]

    def right(self):
        return self._thd or self._chd and self._chd[-1]

    def lbrother(self):
        n = None
        if self._pnt:
            for node in self._pnt._chd:
                if node == self: return n
                n = node
        return n

    def get_lmost_sibling(self):
        if not self._lmost_sibling and self._pnt and self != self._pnt._chd[0]:
            self._lmost_sibling = self._pnt._chd[0]
        return self._lmost_sibling

    lmost_sibling = property(get_lmost_sibling)

    def _coords(self):
        yield self._loc
        for t in self._chd:
            yield from t._coords()

    def _trees(self):
        yield self._tre
        for t in self._chd:
            yield from t._trees()

    def _pairs(self):
        yield (self._loc, self._tre)
        for t in self._chd:
            yield from t._pairs()

    def _svg_t(self):
        xf, yf, o = 100, 100, 100
        x, y = self._loc
        if self._chd:
            b = 'L%i %i' % (o + int(x*xf), o + int(y*yf))
            for t in self._chd:
                yield from t._svg_t()
                yield b
        else:
            yield 'M%i %i' % (o + int(x*xf), o + int(y*yf))

    def _svg(self):
        xf, yf, o = 100, 100, 100
        yield '<svg height="1000" width="1000">\n'
        yield '<path stroke-linecap="round" d="'
        yield from self._svg_t()
        yield '" stroke="black" fill="none" stroke-width="3"/>\n'
        for c, t in self._pairs():
            x = o + int(c[0]*xf)
            y = o + int(c[1]*yf)
            yield '<circle cx="%i" cy="%i" r="15" stroke="black" stroke-width="2" fill="white"/>\n' % (x, y)
            if t._chd:
                l = '"%i,%i %i,%i %i,%i"' % (x-20,y-10,x+20,y-10,x,y-40)
                yield '<polygon points=%s stroke="black" stroke-width="2" fill="yellow"/>\n' % l
                r = 'T' if t._res == True else 'F' if t._res == False else str(t._res)
                yield '<text x="%i" y="%i" style="font-family: helvetica; font-size:12">%s</text>\n' % (x-2 if len(r) == 1 else x-6, y-15, r)
            c = t._chr
            yield '<text x="%i" y="%i" style="font-family: helvetica; font-size:15">%s</text>\n' % (x-4 if len(c) == 1 else x-8, y+4, c)
        yield "</svg>"

    @property
    def svg(self):
        return ''.join(self._svg())

def is_on(a, b, c):
    "Return true iff point c intersects the line segment from a to b."
    # (or the degenerate case that all 3 points are coincident)
    return (collinear(a, b, c)
            and (within(a[0], c[0], b[0]) if a[0] != b[0] else
                 within(a[1], c[1], b[1])))

def collinear(a, b, c):
    "Return true iff a, b, and c all lie on the same line."
    x = (b[0] - a[0]) * (c[1] - a[1])
    y = (c[0] - a[0]) * (b[1] - a[1]) 
    return abs(x-y) < 5

def within(p, q, r):
    "Return true iff q is between p and r (inclusive)."
    return p <= q <= r or r <= q <= p

def buchheim(tree):
    dt = firstwalk(DrawTree(tree))
    min = second_walk(dt)
    if min < 0: third_walk(dt, -min)
    return dt

def third_walk(tree, n):
    tree._loc = (tree._loc[0]+1, tree._loc[1])
    for c in tree._chd:
        third_walk(c, n)

def firstwalk(v, dis=1.):
    if not v._chd:
        if v.lmost_sibling:
            v._loc = (v.lbrother()._loc[0] + dis, v._loc[1])
        else:
            v._loc = (0., v._loc[1])
    else:
        default_anc = v._chd[0]
        for w in v._chd:
            firstwalk(w)
            default_anc = apportion(w, default_anc, dis)
        execute_shifts(v)

        midpoint = (v._chd[0]._loc[0] + v._chd[-1]._loc[0]) / 2

        ell, arr, w = v._chd[0], v._chd[-1], v.lbrother()

        if w:
            v._loc = (w._loc[0] + dis, v._loc[1])
            v._mod = v._loc[0] - midpoint
        else:
            v._loc = (midpoint, v._loc[1])
    return v

def apportion(v, default_anc, dis):
    w = v.lbrother()
    if w == None: return default_anc
    vir = vor = v
    vil, vol = w, v.lmost_sibling
    sir = sor = v._mod
    sil, sol = vil._mod, vol._mod
    while vil.right() and vir.left():
        vil = vil.right()
        vir = vir.left()
        vol = vol.left()
        vor = vor.right()
        vor._anc = v
        shift = (vil._loc[0] + sil) - (vir._loc[0] + sir) + dis
        if shift > 0:
            move_subtree(ancestor(vil, v, default_anc), v, shift)
            sir += shift
            sor += shift
        sil += vil._mod
        sir += vil._mod
        sol += vil._mod
        sor += vil._mod
    if vil.right() and not vor.right():
        vor._thd = vil.right()
        vor._mod += sil - sor
    else:
        if vir.left() and not vol.left():
            vol._thd = vir.left()
            vol._mod += sir - sol
        default_anc = v
    return default_anc

def move_subtree(wl, wr, shift):
    subtrees = wr._num - wl._num
    wr._chg -= shift / subtrees
    wr._sft += shift
    wl._chg += shift / subtrees
    wr._loc = (wr._loc[0]+shift, wr._loc[1])
    wr._mod += shift

def execute_shifts(v):
    shift = change = 0
    for w in v._chd[::-1]:
        w._loc = (w._loc[0] + shift, w._loc[1])
        w._mod += shift
        change += w._chg
        shift += w._sft + change

def ancestor(vil, v, default_anc):
    if vil._anc in v._pnt._chd: return vil._anc
    else: return default_anc

def second_walk(v, m=0, depth=0, minv=None):
    v._loc = (v._loc[0] + m, depth)
    minv = min(v._loc[0], minv) if minv != None else v._loc[0]
    for w in v._chd:
        minv = second_walk(w, m+v._mod, depth+1, minv)
    return minv

from random import randrange

def sized(n):
    if n <= 2: return []
    return [sized(n // 2) for _ in range(randrange(1,n))]


