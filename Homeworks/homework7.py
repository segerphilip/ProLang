############################################################
# HOMEWORK 7
#
# Team members: Hannah Twigg-Smith, Philip Seger
#
# Emails: Hannah.Twigg-Smith@students.olin.edu, Philip.Seger@students.olin.edu
#
# Remarks:
# Deniz Celik helped us with file reading by telling us about pyparsing's
# builtin ReadFile method.
# I wasn't able to figure out why this was, but originally the parser was
# "fast" when matching logic statments. The addition of equality (which required
# me to move some stuff around) made it pretty slow
# Tried to make pCALL an expr but it just wasn't working (spent a lot of time on
# this). As a result, anonymous functions are not called correctly
# Most things work except pSTMT_IF, pSTMT_IFELSE, and pSTMT_FOR, which I mostly
# just ran out of time to implement. (The grammar is correct though)
############################################################

import sys

#
# Expressions
#

class Exp (object):
    pass


class EValue (Exp):
    # Value literal (could presumably replace EInteger and EBoolean)
    def __init__ (self,v):
        self._value = v

    def __str__ (self):
        return "EValue({})".format(self._value)

    def eval (self,env):
        return self._value


class EPrimCall (Exp):
    # Call an underlying Python primitive, passing in Values
    #
    # simplifying the prim call
    # it takes an explicit function as first argument

    def __init__ (self,prim,es):
        self._prim = prim
        self._exps = es

    def __str__ (self):
        return "EPrimCall(<prim>,[{}])".format(",".join([ str(e) for e in self._exps]))

    def eval (self,env):
        vs = [ e.eval(env) for e in self._exps ]
        return apply(self._prim,vs)


class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self,env):
        v = self._cond.eval(env)
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval(env)
        else:
            return self._else.eval(env)


class ELet (Exp):
    # local binding
    # allow multiple bindings
    # eager (call-by-avlue)

    def __init__ (self,bindings,e2):
        self._bindings = bindings
        self._e2 = e2

    def __str__ (self):
        return "ELet([{}],{})".format(",".join([ "({},{})".format(id,str(exp)) for (id,exp) in self._bindings ]),self._e2)

    def eval (self,env):
        new_env = [ (id,e.eval(env)) for (id,e) in self._bindings] + env
        return self._e2.eval(new_env)


class EId (Exp):
    # identifier

    def __init__ (self,id):
        self._id = id

    def __str__ (self):
        return "EId({})".format(self._id)

    def eval (self,env):
        for (id,v) in env:
            if self._id == id:
                return v
        raise Exception("Runtime error: unknown identifier {}".format(self._id))


class ECall (Exp):
    # Call a defined function in the function dictionary

    def __init__ (self,fun,exps):
        self._fun = fun
        self._args = [exp for exp in exps if exp!=","]

    def __str__ (self):
        return "ECall({},[{}])".format(str(self._fun),",".join(str(e) for e in self._args))

    def eval (self,env):
        f = self._fun.eval(env)
        if f.type != "function":
            raise Exception("Runtime error: trying to call a non-function!")
        args = [ e.eval(env) for e in self._args]
        if hasattr(f.env, "type"):
            if f.env.type == "array":
                new_env = zip(f.params,args) + f.env.arr_env
        if len(args) != len(f.params):
            raise Exception("Runtime error: argument # mismatch in call")
        else:
            new_env = zip(f.params,args) + f.env
        return f.body.eval(new_env)


class EFunction (Exp):
    # Creates an anonymous function

    def __init__ (self,params,body):
        self._params = params
        self._body = body

    def __str__ (self):
        return "EFunction([{}],{})".format(",".join(self._params),str(self._body))

    def eval (self,env):
        return VClosure(self._params,self._body,env)


class ERefCell (Exp):
    # this could (should) be turned into a primitive
    # operation.  (WHY?)

    def __init__ (self,initialExp):
        self._initial = initialExp

    def __str__ (self):
        return "ERefCell({})".format(str(self._initial))

    def eval (self,env):
        v = self._initial.eval(env)
        return VRefCell(v)

class EDo (Exp):

    def __init__ (self,exps):
        self._exps = exps

    def __str__ (self):
        return "EDo([{}])".format(",".join(str(e) for e in self._exps))

    def eval (self,env):
        # default return value for do when no arguments
        v = VNone()
        for e in self._exps:
            v = e.eval(env)
        return v

class EWhile (Exp):

    def __init__ (self,cond,exp):
        self._cond = cond
        self._exp = exp

    def __str__ (self):
        return "EWhile({},{})".format(str(self._cond),str(self._exp))

    def eval (self,env):
        c = self._cond.eval(env)
        if c.type != "boolean":
            raise Exception ("Runtime error: while condition not a Boolean")
        while c.value:
            self._exp.eval(env)
            c = self._cond.eval(env)
            if c.type != "boolean":
                raise Exception ("Runtime error: while condition not a Boolean")
        return VNone()

class EFor (Exp):

    def __init__ (self,init,arr,expr):
        self._init = init
        self._arr = arr
        self._expr = expr

    def __str__ (self):
        return "EFor({};{};{}){{}}".format(str(self._init),str(self._cond),str(self._incr),str(self._expr))

    def eval (self,env):
        # doesn't work, we need to increment through self._arr and do expr each
        # time
        env.insert(0, (self._init[0], VRefCell(self._init[1].eval(env))))

        c = self._cond.eval(env)

        if c.type != "boolean":
            raise Exception ("Runtime error: for condition not a Boolean")

        while c.value:
            self._expr.eval(env)
            self._incr.eval(env)
            c = self._cond.eval(env)
            if c.type != "boolean":
                raise Exception ("Runtime error: for condition not a Boolean")
        return VNone()


class EArray (Exp):

    def __init__ (self, content):
        self._content = content

    def __str__(self):
        return "EArray({})".format(str(self._length))

    def eval (self,env):
        values = [item.eval(env) for item in self._content]
        return VArray(values,env)


class EDict (Exp):

    def __init__ (self, content):
        self._content = content

    def __str__(self):
        return "EDict({})".format(str(self._length))

    def eval (self,env):
        keys = []
        values = []
        for index, value in enumerate(self._content):
            if index % 2 == 0:
                keys.append(value)
            else:
                values.append(value.eval(env))

        return VDict(keys,values,env)


class EWith (Exp):

    def __init__ (self,obj,expr):

        self._object = obj
        self._exp = expr

    def __str__ (self):
        return "EWith({},{})".format(str(self._object),str(self._exp))

    def eval (self,env):
        ob = self._object.eval(env)
        if ob.type != "object" and ob.type != "array":
            raise Exception("Runtime error: expected an object")
        specific_env = ob.arr_env + ob.env + env
        return self._exp.eval(specific_env)

#
# Values
#

class Value (object):
    pass


class VInteger (Value):
    # Value representation of integers

    def __init__ (self,i):
        self.value = i
        self.type = "integer"

    def __str__ (self):
        return str(self.value)


class VString (Value):
    # Value representation of strings

    def __init__ (self,i):
        self.value = i
        self.type = "string"

    def __str__ (self):
        return self.value


class VBoolean (Value):
    # Value representation of Booleans

    def __init__ (self,b):
        self.value = b
        self.type = "boolean"

    def __str__ (self):
        return "true" if self.value else "false"


class VClosure (Value):

    def __init__ (self,params,body,env):
        #print params
        self.params = params
        self.body = body
        self.env = env
        self.type = "function"

    def __str__ (self):
        return "<function [{}] {}>".format(",".join(self.params),str(self.body))


class VArray (Value):

    def __init__ (self,content,env):
        self.value = [item for item in content]
        self.type = "array"
        self.env = env

    def __str__ (self):
        b = [thing.value for thing in self.value]
        return str(b)


class VDict (Value):

    def __init__ (self,keys,values,env):
        self.keys = keys
        self.values = values
        self.value = {key: value.value for (key, value) in zip(keys,values)}
        self.type = "dict"
        self.env = env

    def __str__ (self):
        return str(self.value)


class VRefCell (Value):

    def __init__ (self,initial):
        self.content = initial
        self.type = "ref"

    def __str__ (self):
        return "<ref {}>".format(str(self.content))


class VNone (Value):

    def __init__ (self):
        self.type = "none"
        self.value = None

    def __str__ (self):
        return "none"


# Primitive operations

def oper_plus (v1,v2):
    if v1.type == "string" and v2.type == "string":
        return VString(v1.value + v2.value)
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value + v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_minus (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value - v2.value)
    raise Exception ("Runtime error: trying to subtract non-numbers")

def oper_times (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value * v2.value)
    raise Exception ("Runtime error: trying to multiply non-numbers")

def oper_not_equal (v1, v2):
    if v1.type == v2.type:
        return VBoolean(not (v1.value==v2.value))
    raise Exception ("Runtime error: type error in neq")

def oper_deref (v1):
    if v1.type == "ref":
        return v1.content
    raise Exception ("Runtime error: dereferencing a non-reference value")

def oper_print (*v1):
    for arg in v1:
        print arg
    return VNone()

def oper_length (v1):
    if v1.type == "string" or v1.type == "array":
        return VInteger(len(v1.value))
    raise Exception ("Runtime error: type error in length")

def oper_substring (v1,v2,v3):
    if v1.type == "string" and v2.type == "integer" and v3.type == "integer":
        return VString(v1.value[v2.value:v3.value])
    raise Exception ("Runtime error: type error in substring")

def oper_update (v1,v2,v3=None):
    if v1.type == "ref":
        if v1.content.type == "array":
            v1.content.value[v2.value] = v3.value
            return VNone()
        else:
            v1.content.value = v2.value
            return VNone()
    raise Exception ("Runtime error: updating a non-reference value")

def oper_arr_index (v1,v2):
    if v1.type == "ref":
        return v1.content.value[v2.value]
    raise Exception ("Runtime error: updating a non-reference value")

def oper_dict_key (v1,v2):
    if v1.type == "ref":
        return v1.content.value[v2.value]
    raise Exception ("Runtime error: updating a non-reference value")

def oper_index (v1, v2):
    if v1.type == "array" and v2.type =="integer":
        return VInteger(v1.value[v2.value])
    raise Exception ("Runtime error: type error in index")

def oper_not (v1):
    if v1.type == "boolean":
        return VBoolean(not v1.value)
    raise Exception ("Runtime error: type error in not: condition not a boolean")

def oper_and (v1,v2):
    if v1.type == "boolean" and v2.type == "boolean":
        return VBoolean(v1.value and v2.value)
    raise Exception ("Runtime error: type error in and: condition not a boolean")

def oper_or (v1,v2):
    if v1.type == "boolean" and v2.type == "boolean":
        return VBoolean(v1.value or v2.value)
    raise Exception ("Runtime error: type error in or: condition not a boolean")

def oper_less (v1,v2):
    if v1.type == "string" and v2.type == "string":
         return VBoolean(v1.value < v2.value)
    if v1.type == "integer" and v2.type == "integer":
         return VBoolean(v1.value < v2.value)
    raise Exception ("Runtime error: type error in less: types do not match")

def oper_greater (v1,v2):
    if v1.type == "string" and v2.type == "string":
         return VBoolean(v1.value > v2.value)
    if v1.type == "integer" and v2.type == "integer":
         return VBoolean(v1.value > v2.value)
    raise Exception ("Runtime error: type error in greater: types do not match")

def oper_less_equal (v1,v2):
    if v1.type == "string" and v2.type == "string":
         return VBoolean(v1.value <= v2.value)
    if v1.type == "integer" and v2.type == "integer":
         return VBoolean(v1.value <= v2.value)
    raise Exception ("Runtime error: type error in less/equal: types do not match")

def oper_greater_equal (v1,v2):
    if v1.type == "string" and v2.type == "string":
         return VBoolean(v1.value >= v2.value)
    if v1.type == "integer" and v2.type == "integer":
         return VBoolean(v1.value >= v2.value)
    raise Exception ("Runtime error: type error in greater/equal: types do not match")

def oper_equals (v1,v2):
    if v1.type == v2.type:
         return VBoolean(v1.value == v2.value)
    raise Exception ("Runtime error: type error in equal: types do not match")

############################################################
# IMPERATIVE SURFACE SYNTAX
#



##
## PARSER
##
# cf http://pyparsing.wikispaces.com/

from pyparsing import Word, Literal, ZeroOrMore, OneOrMore, Keyword, Forward, alphas, alphanums, NoMatch, Group, QuotedString, Suppress, Optional, FollowedBy, StringEnd


def initial_env_pj ():
    # A sneaky way to allow functions to refer to functions that are not
    # yet defined at top level, or recursive functions
    env = []

    env.insert(0,
               ("len",
                VRefCell(VClosure(["x"],
                                  EPrimCall(oper_length,[EId("x")]),
                                  env))))
    return env




def parse_pj ():
    # Grammar:
    #
    # expr ::= integer literal                   # of the form 123 or -456
    #      boolean literal                       # true , false
    #      string literal                        # of the form "xyz"
    #      id                                    # starts with a letter or _
    #      expr + expr                           # adds integers / concatenates arrays / concatenates strings
    #      expr * expr
    #      expr - expr
    #      expr == expr                          # equality (all types)
    #      expr > expr                           # for integers and strings (lexicographic order)
    #      expr >= expr                          # for integers and strings (lexicographic order)
    #      expr < expr                           # for integers and strings (lexicographic order)
    #      expr <= expr                          # for integers and strings (lexicographic order)
    #      expr <> expr                          # this is "not equal" (all types)
    #      expr and expr                         # short-circuiting
    #      expr or expr                          # short-circuiting
    #      not expr
    #      let ( id = expr , ... ) expr          # local binding
    #      expr ? expr : expr                    # conditional
    #      expr ( expr , ... )                   # function call
    #      ( expr )
    #      [ expr , ... ]                        # creates an array
    #      fun ( id , ... ) body                 # anonymous function
    #      fun id ( id , ... ) body              # recursive anonymous function
    #      { id : expr , ... }                   # dictionary (record)
    #      expr [ expr ]                         # array or string (a[2]) or dictionary (a["x"]) indexing
    #
    #
    # vals ::= integers
    #          Booleans
    #          strings
    #          arrays
    #          dictionaries (records)
    #          functions (closures)
    #          None value
    #
    #
    # stmt ::= expr ;                            # evaluate expression (drop the result)
    #      id = expr ;                           # assignment to a variable
    #      print expr , ... ;                    # print values (on the same line)
    #      expr [ expr ] = expr ;                # assign to array or dictionary element
    #          if ( expr ) body                  # conditional
    #          if ( expr ) body else body        # conditional
    #      while ( expr ) body                   # loop
    #      for ( id in expr ) body               # iteration over elements of an array
    #
    #
    # body ::= { decl ... stmt ... }             # zero of more declarations followed by zero or more statements
    #
    #
    # decl ::= var id ;
    #          var id = expr ;
    #          def id ( id , ... ) body          # function definition


    # Don't allow ids to have any characters like +-=*!? because it confuses the
    # parser when there aren't spaces betwee things
    idChars = alphas+"_"

    pIDENTIFIER = Word(idChars, idChars+"0123456789")
    #### NOTE THE DIFFERENCE
    pIDENTIFIER.setParseAction(lambda result: EPrimCall(oper_deref,[EId(result[0])]))

    # A name is like an identifier but it does not return an EId...
    pNAME = Word(idChars,idChars+"0123456789")

    pNAMES = ZeroOrMore(pNAME)
    pNAMES.setParseAction(lambda result: [result])

    pINTEGER = Word("0123456789")
    pINTEGER.setParseAction(lambda result: EValue(VInteger(int(result[0]))))

    pSTRING = QuotedString('"')
    pSTRING.setParseAction(lambda result: EValue(VString(result[0])))

    pBOOLEAN = Keyword("true") | Keyword("false")
    pBOOLEAN.setParseAction(lambda result: EValue(VBoolean(result[0]=="true")))

    pEXPR = Forward()

    pPAREN = "(" + pEXPR + ")"
    pPAREN.setParseAction(lambda result: result[1])

    pEXPRS = ZeroOrMore(pEXPR)
    pEXPRS.setParseAction(lambda result: [result])

    pNOT = (Keyword("not") + pEXPR)
    pNOT.setParseAction(lambda result: EPrimCall(oper_not, [result[1]]))

    pCORE = ( pPAREN | pNOT | pINTEGER | pSTRING | pBOOLEAN | pIDENTIFIER )

    pFACTOR = Forward()

    pBODY = Forward()

    pSTEP = Forward()

    pTIMES = (pCORE + "*" + pFACTOR)
    pTIMES.setParseAction(lambda result: EPrimCall(oper_times,[result[0],result[2]]))

    pEQUALITY = (pCORE + "==" + pSTEP)
    pEQUALITY.setParseAction(lambda result: EPrimCall(oper_equals, [result[0],result[2]]))

    pGT = (pCORE + ">" + pSTEP)
    pGT.setParseAction(lambda result: EPrimCall(oper_greater, [result[0],result[2]]))

    pGEQ = (pCORE + ">=" + pSTEP)
    pGEQ.setParseAction(lambda result: EPrimCall(oper_greater_equal, [result[0],result[2]]))

    pLT = (pCORE + "<" + pSTEP)
    pLT.setParseAction(lambda result: EPrimCall(oper_less, [result[0],result[2]]))

    pLEQ = (pCORE + "<=" + pSTEP)
    pLEQ.setParseAction(lambda result: EPrimCall(oper_less_equal, [result[0],result[2]]))

    pNEQ = (pCORE + "<>" + pSTEP)
    pNEQ.setParseAction(lambda result: EPrimCall(oper_not_equal, [result[0],result[2]]))

    pSTEP << ( pEQUALITY | pGT | pGEQ | pLT | pLEQ | pNEQ | pCORE )

    pAND = (pSTEP + Keyword("and") + pFACTOR)
    pAND.setParseAction(lambda result: EPrimCall(oper_and, [result[0],result[2]]))

    pOR = (pSTEP + Keyword("or") + pFACTOR)
    pOR.setParseAction(lambda result: EPrimCall(oper_or, [result[0],result[2]]))

    pCOND = pCORE + "?" + pEXPR + ":" + pEXPR
    pCOND.setParseAction(lambda result: EIf(result[0], result[2], result[4]))

    pFACTOR << ( pTIMES | pCOND | pAND | pOR | pSTEP )

    pTERM = Forward()

    pPLUS = (pFACTOR + "+" + pTERM)
    pPLUS.setParseAction(lambda result: EPrimCall(oper_plus,[result[0],result[2]]))

    pMINUS = (pFACTOR + "-" + pTERM)
    pMINUS.setParseAction(lambda result: EPrimCall(oper_minus,[result[0],result[2]]))

    pTERM << ( pMINUS | pPLUS | pFACTOR )

    pDICT = "{" + ZeroOrMore(pNAME + Suppress(":") + pEXPR + Suppress(",")) + Optional(pNAME + Suppress(":") + pEXPR) + "}"
    pDICT.setParseAction(lambda result: EDict(result[1:-1]))

    pARRAY = "[" + ZeroOrMore(pEXPR + Suppress(",")) + Optional(pEXPR) + "]"
    pARRAY.setParseAction(lambda result: EArray(result[1:-1]))

    pARR_INDEX = pNAME + "[" + pEXPR + "]"
    pARR_INDEX.setParseAction(lambda result: EPrimCall(oper_arr_index, [EId(result[0]), result[2]]))

    pDICT_KEY = pNAME + "[" + pSTRING + "]"
    pDICT_KEY.setParseAction(lambda result: EPrimCall(oper_dict_key, [EId(result[0]), result[2]]))

    def mkFunBody (params,body):
        bindings = [ (p,ERefCell(EId(p))) for p in params ]
        return ELet(bindings,body)

    pFUN = Keyword("fun") + "(" + Group(Optional(pNAME) + ZeroOrMore(Suppress(",") + pNAME)) + ")" + pBODY
    pFUN.setParseAction(lambda result: EFunction(result[2],mkFunBody(result[2],result[4])))

    def parse_let(result):
        bindings = [(result[2],ERefCell(result[4]))]
        for vs in result[5]:
            bindings.append((vs[0],ERefCell(vs[2])))
        return ELet(bindings,result[7])

    pLET = Keyword("let") + "(" + pNAME + "=" + pEXPR + Group(ZeroOrMore( Suppress(",") + Group(pNAME + "=" + pEXPR) ))+ ")" + pEXPR
    pLET.setParseAction(parse_let)

    pEXPR << ( pFUN | pLET | pARRAY | pDICT | pARR_INDEX | pDICT_KEY | pTERM )

    pDECL_VAR = "var" + pNAME + ";"
    pDECL_VAR.setParseAction(lambda result: (result[1], VNone)) # TODO this declaration as VNone is probably wrong

    pDECL_VAR_VAL = "var" + pNAME + "=" + pEXPR + ";"
    pDECL_VAR_VAL.setParseAction(lambda result: (result[1],result[3]))

    pSTMT = Forward()

    pSTMTS = ZeroOrMore(pSTMT) + ";"
    pSTMTS.setParseAction(lambda result: [result])

    pDECL_FUN = Keyword("def") + pNAME + "(" + Group(Optional(pNAME) + ZeroOrMore(Suppress(",") + pNAME)) + ")" + pBODY
    pDECL_FUN.setParseAction(lambda result: (result[1], EFunction(result[3],mkFunBody(result[3],result[5]))))

    pDECL = ( pDECL_VAR | pDECL_VAR_VAL | pDECL_FUN | NoMatch() )

    pDECLS = ZeroOrMore(pDECL)
    pDECLS.setParseAction(lambda result: [result])

    pSTMT_ID = pNAME + "=" + pEXPR + ";"
    pSTMT_ID.setParseAction(lambda result: EPrimCall(oper_update,[EId(result[0]),result[2]]))

    pSTMT_PRINT = "print" + pEXPR + ZeroOrMore("," + pEXPR) + ";"
    pSTMT_PRINT.setParseAction(lambda result: EPrimCall(oper_print,[v for (i, v) in enumerate(result) if (i % 2) != 0]))

    pSTMT_WHILE = Keyword("while") + pEXPR + pBODY
    pSTMT_WHILE.setParseAction(lambda result: EWhile(result[1],result[2]))

    pSTMT_IF = Keyword("if") + pEXPR + pBODY
    pSTMT_IF.setParseAction(lambda result: EIf(result[1],result[2],EValue(VBoolean(True))))

    pSTMT_IFELSE = Keyword("if") + pEXPR + pBODY + Keyword("else") + pBODY
    pSTMT_IFELSE.setParseAction(lambda result: EIf(result[1],result[2],result[4]))

    pSTMT_UPDATE = pNAME + "[" + pEXPR + "]" + "=" + pEXPR + ";"
    pSTMT_UPDATE.setParseAction(lambda result: EPrimCall(oper_update,[EId(result[0]),result[2],result[5]]))

    def mkBlock (decls,stmts):
        bindings = [ (n,ERefCell(expr)) for (n,expr) in decls ]
        return ELet(bindings,EDo(stmts))

    pSTMT_BLOCK = "{" + pDECLS + pSTMTS + "}"
    pSTMT_BLOCK.setParseAction(lambda result: mkBlock(result[1],result[2]))

    pSTMT_FOR = Keyword("for") + "(" + pNAME + Keyword("in") + pEXPR + ")" + pBODY
    pSTMT_FOR.setParseAction(lambda result: EFor(result[2],result[4],result[6]))

    pSTMT_EXPR = pEXPR + ";"
    pSTMT_EXPR.setParseAction(lambda result: result[0])

    pCALL = pEXPR + "(" + Group(ZeroOrMore(pEXPR + Optional(","))) + ")" + ";"
    pCALL.setParseAction(lambda result: ECall(result[0], result[2]))

    pSTMT << ( pSTMT_BLOCK | pSTMT_PRINT | pSTMT_IF | pSTMT_IFELSE | pCALL | pSTMT_FOR | pSTMT_WHILE | pSTMT_ID | pSTMT_UPDATE | pSTMT_EXPR )

    pBODY << "{" + Group(ZeroOrMore(pDECL)) + Group(ZeroOrMore(pSTMT)) + "}"
    pBODY.setParseAction(lambda result: mkBlock(result[1],result[2]))

    pTOP_STMT = pSTMT.copy()
    pTOP_STMT.setParseAction(lambda result: {"result":"statement",
                                             "stmt":result[0]})

    pTOP_DECL = pDECL.copy()
    pTOP_DECL.setParseAction(lambda result: {"result":"declaration",
                                             "decl":result[0]})

    pABSTRACT = "#abs" + pSTMT
    pABSTRACT.setParseAction(lambda result: {"result":"abstract",
                                             "stmt":result[1]})

    pQUIT = Keyword("#quit")
    pQUIT.setParseAction(lambda result: {"result":"quit"})

    pTOP = OneOrMore( pTOP_DECL | pTOP_STMT )# + FollowedBy(StringEnd())

    # result = pTOP.parseString(input)[0]
    # return result    # the first element of the result is the expression
    return pTOP

def execute_shell(env, inp):
    try:
        result = inp
        if result["result"] == "statement":
            stmt = result["stmt"]
            # print "Abstract representation:", exp
            v = stmt.eval(env)

        elif result["result"] == "abstract":
            print result["stmt"]

        elif result["result"] == "quit":
            return

        elif result["result"] == "declaration":
            (name,expr) = result["decl"]
            v = expr.eval(env)
            env.insert(0,(name,VRefCell(v)))
            print "{} defined".format(name)


    except Exception as e:
        print "Exception: {}".format(e)


def execute(filename):
    #lines = [line.rstrip('\n') for line in open(filename)]
    result = parse_pj().parseFile(filename)
    env = initial_env_pj()
    call_main = {'result': 'statement', 'stmt': ECall(EPrimCall(oper_deref,[EId("main")]),[])}
    result.append(call_main)

    for res in result:
        execute_shell(env, res)


if __name__ == '__main__':
    if len(sys.argv)>1:
        execute(sys.argv[1])
