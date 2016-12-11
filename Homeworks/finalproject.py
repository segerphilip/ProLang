############################################################
# FINAL PROJECT
#
# Team members: Hannah Twigg-Smith, Philip Seger
#
# Emails: Hannah.Twigg-Smith@students.olin.edu, Philip.Seger@students.olin.edu
#
# Remarks:
# We weren't super sure how to store constants and variables in the environment.
# True prolog finds unifications sequentially, in that it only finds another
# match once you tell it to. Ours returns all possible matches.
#
############################################################
# Prolog-style interpreter
#

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


class EQuery (Exp):
    # Queries

    def __init__ (self,name,var):
        self._name = name

        if type(var) != list:
            self._vars = var.asList()
        else:
            self._vars = var

    def __str__ (self):
        return "EQuery({},{})".format(self._name,self._vars)

    def eval (self,env):
        matches = []

        # check if we're evaluating a rule
        if type(env[self._name]) == dict:
            possible_matches = []

            local_env = dict(zip(env[self._name]["vars"],self._vars))

            for rel in env[self._name]["body"]:
                rel = list(rel)
                rel[1] = rel[1].asList()

                for i,v in enumerate(rel[1]):
                    if v in local_env:
                        rel[1][i] = local_env[v]
                    elif v[0].isupper:
                        print "INTERMEDIATE VARIABLE"


                # print rel
                # print "MATCHES"
                # print rel[1]
                if not EQuery(rel[0],rel[1]).eval(env):
                    return "no"
                #possible_matches.append(EQuery(rel[0],rel[1]).eval(env))

            #matches = possible_matches
            return "yes"





        if len(self._vars) != len(env[self._name][0]):
            return "Error: Incorrect number of arguments"

        cont_vars = False
        var_positions = []

        for word in self._vars:
            if word[0].isupper():
                cont_vars = True
                var_positions.append(True)
            else:
                var_positions.append(False)

        #attempt to unify terms
        if cont_vars:

            for relation in env[self._name]:
                match = True
                for pos, var, rel in zip(var_positions, self._vars, relation):
                    if pos:
                        continue
                    elif var == rel:
                        continue
                    else:
                        match = False
                if match:
                    matches.append(relation)

            return matches

        else:
            if self._vars in env[self._name]:
                return True
            return False


class EVariable (Exp):
    # Variables

    def __init__ (self,val):
        self._name = name
        self._val = val

    def __str__ (self):
        return "EVariable({})".format(self._name)

    def eval (self,env):
        pass



class EConstant (Exp):
    # Constants

    def __init__ (self,val):
        self._name = name
        self._val = val

    def __str__ (self):
        return "EConstant({})".format(self._name)

    def eval (self,env):
        pass



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


class VConstant (Value):
    # Value representation of constant

    def __init__ (self,i):
        self.value = i
        self.type = "constant"

    def __str__ (self):
        return self.value


class VVariable (Value):
    # Value representation of constant

    def __init__ (self,i):
        self.value = i
        self.type = "variable"

    def __str__ (self):
        return self.value


class VBoolean (Value):
    # Value representation of Booleans

    def __init__ (self,b):
        self.value = b
        self.type = "boolean"

    def __str__ (self):
        return "true" if self.value else "false"


class VNone (Value):

    def __init__ (self):
        self.type = "none"
        self.value = None

    def __str__ (self):
        return "none"


# Primitive operations

def oper_plus (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value + v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")


############################################################
# Pylog SURFACE SYNTAX
#



##
## PARSER
##
# cf http://pyparsing.wikispaces.com/

from pyparsing import Word, Literal, ZeroOrMore, OneOrMore, Keyword, Forward, alphas, alphanums, NoMatch, Group, QuotedString, Suppress, Optional


def initial_env_imp ():
    # A sneaky way to allow functions to refer to functions that are not
    # yet defined at top level, or recursive functions
    env = {}

    return env



def parse_imp (input):
    # parse a string into an element of the abstract representation

    # plan on implementing:
    # facts, rules, relations, queries

    # Grammar:
    #
    # <expr> ::= <integer>
    #            true
    #            false
    #            <identifier>
    #            ( if <expr> <expr> <expr> )
    #            ( function ( <name ... ) <expr> )
    #            ( <expr> <expr> ... )
    #
    # <decl> ::= var name = expr ;
    #
    # <stmt> ::= name ( constant, ... )
    #


    idChars = alphas+"_+*!=<>"
    capitals = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowers = "abcdefghijklmnopqrstuvwxyz"

    def checkCapital (word):
        if word[0].isupper():
            return VVariable(word)
        else:
            return VConstant(word)

    pNAME = Word(idChars,idChars+"0123456789")
    #pNAME.setParseAction(lambda result: checkCapital(result[0]))

    pNAMES = ZeroOrMore(pNAME)
    pNAMES.setParseAction(lambda result: [result])

    pINTEGER = Word("0123456789")
    pINTEGER.setParseAction(lambda result: EValue(VInteger(int(result[0]))))

    pSTRING = QuotedString('"')
    pSTRING.setParseAction(lambda result: EValue(VString(result[0])))

    pBOOLEAN = Keyword("true") | Keyword("false")
    pBOOLEAN.setParseAction(lambda result: EValue(VBoolean(result[0]=="true")))

    pEXPR = Forward()

    pEXPRS = ZeroOrMore(pEXPR)
    pEXPRS.setParseAction(lambda result: [result])

    pEXPR << ( pINTEGER | pBOOLEAN | pSTRING )

    pSTMT = Forward()

    pDECL_FACT = pNAME + "."
    pDECL_FACT.setParseAction(lambda result: (result[0], result[2]))

    pRELATION = pNAME + "(" + Group(pNAME + ZeroOrMore(Suppress(",") + pNAME)) + ")"
    pRELATION.setParseAction(lambda result: (result[0], result[2]))

    pDECL_RELATION = pRELATION + "."
    pDECL_RELATION.setParseAction(lambda result: result[0])

    pRULE = pRELATION + ":-" + Group(pRELATION + ZeroOrMore(Suppress(",") + pRELATION)) + "."
    pRULE.setParseAction(lambda result: (result[0], result[2]))

    pDECL = ( pDECL_FACT ^ pDECL_RELATION ^ NoMatch() )

    pSTMT_QUERY = pRELATION + "?"
    pSTMT_QUERY.setParseAction(lambda result: EQuery(result[0][0], result[0][1]))

    pSTMT << ( pSTMT_QUERY )

    pTOP_STMT = pSTMT.copy()
    pTOP_STMT.setParseAction(lambda result: {"result":"statement",
                                             "stmt":result[0]})

    pTOP_RULE = pRULE.copy()
    pTOP_RULE.setParseAction(lambda result: {"result":"rule",
                                             "rule":result})

    pTOP_DECL = pDECL.copy()
    pTOP_DECL.setParseAction(lambda result: {"result":"declaration",
                                             "decl":result[0]})

    pQUIT = Keyword("#quit")
    pQUIT.setParseAction(lambda result: {"result":"quit"})

    pTOP = (pQUIT ^ pTOP_RULE ^ pTOP_DECL ^ pTOP_STMT)

    result = pTOP.parseString(input)[0]
    return result    # the first element of the result is the expression


def shell ():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Final Project - Prolog-type Language"
    print "#quit to quit, #abs to see abstract representation"
    env = initial_env_imp()


    while True:
        inp = raw_input("pylog> ")

        try:
            result = parse_imp(inp)

            if result["result"] == "statement":
                stmt = result["stmt"]
                v = stmt.eval(env)
                print v

            elif result["result"] == "quit":
                return

            elif result["result"] == "rule":
                res = result["rule"].asList()
                res = (res[0], res[2])

                env[res[0][0]] = {"vars":res[0][1].asList(),
                                  "body":res[1]}

                print "Rule {} defined".format(res[0][0])

            elif result["result"] == "declaration":
                (name, constants) = result["decl"]
                cont_vars = False

                for constant in constants:
                    if constant[0].isupper():
                        cont_vars = True

                if name in env:
                    env[name].append(constants.asList())
                elif cont_vars:
                    print "Error: can't define a relation with a variable"
                else:
                    env[name] = [constants.asList()]
                    print "Relation {} defined".format(name)


        except Exception as e:
            print "Exception: {}".format(e)

if __name__ == '__main__':
    shell()
