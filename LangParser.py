from Parser import *
from Do import do

lower_set = 'abcdefghijklmnopqrstuvwxyz'
upper_set = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
numbr_set = '1234567890'
alpha_set = lower_set + upper_set
alpnm_set = alpha_set + numbr_set

lowercase = oneOf(lower_set)
uppercase = oneOf(upper_set)
letter = oneOf(alpha_set)
alphanum = oneOf(alpnm_set)

@do(Parser)
def between(p,l,r):
    yield l
    x = yield p
    yield r
    yield Parser.pure(x)

lbrack = matchString('(')
rbrack = matchString(')')
parens = between(many(alphanum), lbrack, rbrack)
print(parens()('(abc'))
print(parens()('(abc)'))
