from functools import reduce
class AST:

    def __init__(self, result, op=None, children=[]):
        self._res = result
        self._opr = op
        self._chd = children
        self._chr = str(result) if type(result) == int else str(result)[0]

    def __repr__(self):
        return ''.join(buchheim(self)._svg())

class DrawTree:

    def __init__(self, tree, parent=None, depth=0, number=1):
        self._x = -1.
        self._y = depth
        self._tre = tree
        self._chd = [DrawTree(c, self, depth+1, i+1) for i, c in
                     enumerate(tree._chd)]
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

    def _pairs(self):
        yield (self._x, self._y, self._tre)
        for t in self._chd:
            yield from t._pairs()

    def _svg_edges(self, xfac, yfac, xofs, yofs):
        x, y = self._x, self._y
        if self._chd:
            b = 'L%i %i' % (xofs + int(x*xfac), yofs - int(y*yfac))
            for t in self._chd:
                yield from t._svg_edges(xfac, yfac, xofs, yofs)
                yield b
        else:
            yield 'M%i %i' % (xofs + int(x*xfac), yofs - int(y*yfac))

    def _svg(self, xh=700, yh=700):
        xmax, ymax = self.corner()
        xofs = 100
        yofs = yh - xofs
        xfac, yfac = ((xh-2*xofs) / xmax if xmax else xh/2), (yh-2*xofs) / ymax if ymax else yh/2
        yield '<svg height="%i" width="%i">\n' % (xh, yh)
        yield '<path stroke-linecap="round" d="'
        yield from self._svg_edges(xfac, yfac, xofs, yofs)
        yield '" stroke="black" fill="none" stroke-width="3"/>\n'
        for x, y, t in self._pairs():
            x, y, c = xofs + int(x*xfac), yofs - int(y*yfac), t._chr
            if t._chd:
                ht,bs,ts,r = 30,20,5,t._opr
                yield '<polygon points='
                yield '"%i,%i %i,%i %i,%i"' % (x-bs,y-ht,x+bs,y-ht,x,y-ts)
                yield ' stroke="black" stroke-width="2" fill="yellow"/>\n'
                yield '<text x="%i" y="%i" ' % (x - len(r) * 3, y-18)
                yield 'style="font-family: courier; font-size:12">%s</text>' % r
            yield '<circle cx="%i" cy="%i" ' % (x, y)
            yield 'r="15" stroke="black" stroke-width="2" fill="white"/>\n'
            yield '<text x="%i" y="%i" ' % (x - len(c) * 4, y+5)
            yield 'style="font-family: helvetica; font-size:15">%s</text>' % c
        yield "</svg>"

    def corner(self):
        xmax, ymax = self._x, self._y
        for t in self._chd:
            txmx, tymx = t.corner()
            xmax = max(txmx, xmax)
            ymax = max(tymx, ymax)
        return xmax, ymax

def buchheim(tree):
    dt = firstwalk(DrawTree(tree))
    min = second_walk(dt)
    if min < 0: third_walk(dt, -min)
    return dt

def third_walk(tree, n):
    tree._x += 1
    for c in tree._chd:
        third_walk(c, n)

def firstwalk(v, dis=1.):
    if not v._chd:
        if v.lmost_sibling:
            v._x = v.lbrother()._x + dis
        else:
            v._x = 0.
    else:
        default_anc = v._chd[0]
        for w in v._chd:
            firstwalk(w)
            default_anc = apportion(w, default_anc, dis)
        execute_shifts(v)
        midpoint = (v._chd[0]._x + v._chd[-1]._x) / 2
        ell, arr, w = v._chd[0], v._chd[-1], v.lbrother()
        if w:
            v._x = w._x + dis
            v._mod = v._x - midpoint
        else:
            v._x = midpoint
    return v

def apportion(v, default_anc, dis):
    w = v.lbrother()
    if w == None: return default_anc
    vir = vor = v
    vil, vol = w, v.lmost_sibling
    sir = sor = v._mod
    sil, sol = vil._mod, vol._mod
    while vil.right() and vir.left():
        vil, vir, vol, vor = vil.right(), vir.left(), vol.left(), vor.right()
        vor._anc = v
        shift = (vil._x + sil) - (vir._x + sir) + dis
        if shift > 0:
            wl = ancestor(vil, v, default_anc)
            subtrees = v._num - wl._num
            v._chg -= shift / subtrees
            v._sft += shift
            wl._chg += shift / subtrees
            v._x += shift
            v._mod += shift
            sir += shift
            sor += shift
        sil += vil._mod
        sir += vir._mod
        sol += vol._mod
        sor += vor._mod
    if vil.right() and not vor.right():
        vor._thd = vil.right()
        vor._mod += sil - sor
    else:
        if vir.left() and not vol.left():
            vol._thd = vir.left()
            vol._mod += sir - sol
        default_anc = v
    return default_anc

def execute_shifts(v):
    shift = change = 0
    for w in v._chd[::-1]:
        w._x += shift
        w._mod += shift
        change += w._chg
        shift += w._sft + change

def ancestor(vil, v, default_anc):
    return vil._anc if vil._anc in v._pnt._chd else default_anc

def second_walk(v, m=0, depth=0, minv=None):
    v._x += m
    v._y = depth
    minv = min(v._x, minv) if minv != None else v._x
    for w in v._chd:
        minv = second_walk(w, m+v._mod, depth+1, minv)
    return minv
