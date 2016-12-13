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

#
# Expressions
#

class Exp (object):
    pass

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

                ans = EQuery(rel[0],rel[1]).eval(env)

                if ans == "no":
                    return ans
                else:
                    continue

                #return (self._name,ans[1])

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

            return (self._name, matches)

        else:
            if self._vars in env[self._name]:
                return "yes"
            return "no"



############################################################
# Pylog SURFACE SYNTAX
#



##
## PARSER
##
# cf http://pyparsing.wikispaces.com/

from pyparsing import Word, Literal, ZeroOrMore, OneOrMore, Keyword, Forward, alphas, alphanums, NoMatch, Group, QuotedString, Suppress, Optional


def initial_env_imp ():
    # environment is defined as a dictionary
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
    #
    # <decl> ::= var name = expr ;
    #
    # <stmt> ::= name ( constant, ... )
    #


    idChars = alphas+"_+*!=<>"
    capitals = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowers = "abcdefghijklmnopqrstuvwxyz"

    pNAME = Word(idChars,idChars+"0123456789")

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

                if v == "yes" or v == "no":
                    print v
                else:
                    for i in v[1]:
                        print "{}{}.".format(v[0],tuple(i))

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
