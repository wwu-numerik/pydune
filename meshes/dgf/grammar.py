
from pyparsing import ( Optional, oneOf, 
	Dict, Literal, Word, printables, Group, 
	OneOrMore, ZeroOrMore, FollowedBy, Keyword,
	Suppress,LineEnd, White,alphanums,alphas,
	CaselessLiteral, Combine, nums, Or,
	srange, Regex, Each,ParseFatalException)


def indexCheck(minval=0):
	def indexCheckParseAction(string, loc, tokens):
		parsedval = tokens[0]
		print('dewip')
		if parsedval < minval:
			raise ParseFatalException(string, loc, 
					"index %d must be >=0" % (parsedval))
		return parsedval
	return indexCheckParseAction

e = CaselessLiteral('E')
plusorminus = Literal('+') | Literal('-')
number = Word(nums) 
integer = Combine( Optional(plusorminus) + number ).setParseAction(lambda t:int(t[0]))
index = integer.copy().addParseAction(indexCheck(0))
floatnumber = Combine( integer +
                       Optional( Literal('.') + Optional(number) ) +
                       Optional( e + integer )
                     ).setParseAction(lambda t:float(t[0]))

#comment = Suppress("%") + Word(alphanums + " ") 
comment = Regex(r"%.*").setName("comment").suppress()
linend = Or( [comment , LineEnd()] ).suppress()
section_end = (Literal('#') + LineEnd()).suppress()

vertex = (Group( OneOrMore( floatnumber('point') + OneOrMore( White() ).suppress() ) ) + linend)('vertex')
vertex_header = (Keyword('VERTEX') + linend).suppress()
vertex_section = vertex_header + Group(OneOrMore( vertex ))('vertices') + section_end

simplex = (Group( OneOrMore( index('index') + OneOrMore( White() ).suppress() ) ) + linend)('simplex')
simplex_header = (Keyword('SIMPLEX') + linend).suppress()
simplex_section = simplex_header + Group(OneOrMore( simplex ))('simplices') + section_end

boundarysegment = (Group( index('id') + OneOrMore( index('index') + OneOrMore( White() ).suppress() ) ) + linend)('boundarysegment')
boundarysegment_header = (Keyword('BOUNDARYSEGMENTS') + linend).suppress()
boundarysegment_section = boundarysegment_header+ Dict(OneOrMore( boundarysegment ))('boundarysegments') + section_end


sections = Each( [vertex_section, simplex_section, boundarysegment_section] )
dgf_header = (Keyword('DGF') + linend).suppress()
dgf = (dgf_header + Dict(sections) + OneOrMore( section_end ))('dgf')

