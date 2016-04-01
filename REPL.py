#!/usr/local/bin/python3

from cgitb import enable
enable()

from cgi import FieldStorage, escape
from LangParser import expr, bexpr


print('Content-Type: text/html')

print()

form = FieldStorage()

nums = form.getfirst('number')
bols = form.getfirst('bool')

print('<!DOCTYPE html>\n<html lang="en"><head><title>Expressions</title></head><body>')
print('<form action="REPL.py" method="get">')
print('<label for="number">Aritmetic expression:</label>')
print('<input type="text" name="number" id="number" value="%s"><br>' % (escape(nums) if nums else ''))
print('<label for="bool">Boolean expression:</label>')
print('<input type="text" name="bool" id="bool" value="%s">' % (escape(bols) if bols else ''))
print('<input type="submit" value="submit"></form>')
print('<br>')

def show(parser, text):
    print('<code>', escape(text), '</code>')
    print('<br>')
    res = parser()._run([str.encode(text), None], (0,0))
    if res: print(res)
    else:
        print('<code>', ''.join('^' if i == res._loc[1] else '&nbsp;' for i in range(len(text))))
        print('<br>')
        print('<br>'.join(str(res).split('\n')))
        print('</code>')
    print('<br><br>')

if nums: show(expr, nums)
if bols: show(bexpr, bols)

print('</body></html>')

