############################################################
# FINAL PROJECT
#
# Team members: Hannah Twigg-Smith, Philip Seger
#
# Emails: Hannah.Twigg-Smith@students.olin.edu, Philip.Seger@students.olin.edu
#
# Remarks:
# Started with a homework 3-esque structure, and had to essentially work
# backwards, scrapping all of it.
# We weren't super sure how to store constants and variables in the environment,
# so it's a dictionary of nested lists.
# True prolog finds unifications sequentially, in that it only finds another
# match once you tell it to. Ours returns all possible matches.
#
############################################################
# Prolog-style interpreter
#

def check_for_vars(body):
    cont_vars = False
    var_positions = []

    for word in body:
        if word[0].isupper():
            cont_vars = True
            var_positions.append(True)
        else:
            var_positions.append(False)

    return cont_vars, var_positions


def unify_relation(relations, rules, name, body):
    if len(body) != len(relations[name][0]):
        return "Error: Incorrect number of arguments"

    cont_vars, var_positions = check_for_vars(body)
    matches = []

    #attempt to unify terms
    if cont_vars:
        #if the query body contains variables, find matching facts

        for relation in relations[name]:
            match = True
            for pos, var, rel in zip(var_positions, body, relation):
                if pos:
                    continue
                elif var == rel:
                    continue
                else:
                    match = False
            if match:
                matches.append(relation)

        return (name, matches)

    #return yes or no if there are only constants
    if body in relations[name]:
        return "yes"
    return "no"


def unify_rule(relations, rules, name, body):

    local_env = dict(zip(rules[name]["vars"],body))

    for rel in rules[name]["body"]:
        rel = list(rel)
        rel[1] = rel[1].asList()

        for i,v in enumerate(rel[1]):
            if v in local_env:
                rel[1][i] = local_env[v]
            elif v[0].isupper:
                print "INTERMEDIATE VARIABLE"

        ans = top_unify(relations,rules,rel[0],rel[1])

        if ans == "no":
            return ans
        else:
            continue

    return "yes"


def top_unify(relations, rules, name, body):
    matches = []

    if name in relations:
        return unify_relation(relations, rules, name, body)

    elif name in rules:
        return unify_rule(relations, rules, name, body)

    else:
        return "Error: {} not found in environment.".format(name)



############################################################
##
## Pylog parser
##
# cf http://pyparsing.wikispaces.com/

from pyparsing import Word, ZeroOrMore, Keyword, alphas, NoMatch, Group, Suppress


def initial_env ():
    # environment is defined as a dictionary
    relations = {}
    rules = {}

    return relations, rules


def parse_imp (input):
    # Grammar:
    #
    # <expr> ::= <integer>
    #            true
    #            false
    #            <identifier>
    #
    # <fact> ::= relation(constant, ...).
    #
    # <rule> ::= name(constant, ... ) :- name(constant, ...), ... .
    #

    idChars = alphas+"_+*!=<>"

    pNAME = Word(idChars,idChars+"0123456789")

    pRELATION = pNAME + "(" + Group(pNAME + ZeroOrMore(Suppress(",") + pNAME)) + ")"
    pRELATION.setParseAction(lambda result: (result[0], result[2]))

    pDECL_RELATION = pRELATION + "."
    pDECL_RELATION.setParseAction(lambda result: result[0])

    pRULE = pRELATION + ":-" + Group(pRELATION + ZeroOrMore(Suppress(",") + pRELATION)) + "."
    pRULE.setParseAction(lambda result: (result[0], result[2]))

    pFACT = ( pDECL_RELATION ^ NoMatch() )

    pQUERY = pRELATION + "?"
    pQUERY.setParseAction(lambda result: (result[0][0], result[0][1]))

    pTOP_QUERY = pQUERY.copy()
    pTOP_QUERY.setParseAction(lambda result: {"result":"query",
                                             "stmt":result[0]})

    pTOP_RULE = pRULE.copy()
    pTOP_RULE.setParseAction(lambda result: {"result":"rule",
                                             "rule":result})

    pTOP_FACT = pFACT.copy()
    pTOP_FACT.setParseAction(lambda result: {"result":"fact",
                                             "decl":result[0]})

    pQUIT = Keyword("#quit")
    pQUIT.setParseAction(lambda result: {"result":"quit"})

    pENV = Keyword("#env")
    pENV.setParseAction(lambda result: {"result":"env"})

    pTOP = (pQUIT ^ pENV ^ pTOP_RULE ^ pTOP_FACT ^ pTOP_QUERY)

    result = pTOP.parseString(input)[0]
    return result    # the first element of the result is the expression


def shell ():
    # A simple shell
    # Repeatedly read a line of input, parse it, and evaluate the result

    print "Final Project - Prolog-type Language"
    print "#quit to quit"
    relations, rules = initial_env()

    while True:
        inp = raw_input("pylog> ")

        try:
            result = parse_imp(inp)

            if result["result"] == "query":
                head, body = result["stmt"]
                v = top_unify(relations, rules, head, body.asList())

                if v == "yes" or v == "no" or v[0:5] == "Error":
                    print v
                else:
                    for i in v[1]:
                        print "{}{}.".format(v[0],tuple(i))

            elif result["result"] == "quit":
                return

            elif result["result"] == "env":
                print "Relations:"
                print relations
                print "Rules:"
                print rules

            elif result["result"] == "rule":
                res = result["rule"].asList()
                res = (res[0], res[2])

                # Allow multiple rule bodies for recursive rules
                # if res[0][0] in rules:
                #     rules[res[0][0]]["body"].append(res[1])

                # else:
                # Maybe later

                rules[res[0][0]] = {"vars":res[0][1].asList(),
                                    "body":res[1]}

                print "Rule {} defined".format(res[0][0])

            elif result["result"] == "fact":
                (name, constants) = result["decl"]
                cont_vars = False

                for constant in constants:
                    if constant[0].isupper():
                        cont_vars = True
                        break

                if cont_vars:
                    print "Error: Can't define a fact with a variable!"
                elif name in relations:
                    if len(constants) != len(relations[name][0]):
                        print "Error: Relation {} takes {} argument(s), {} given.".format(name,len(relations[name][0]),len(constants))
                    else:
                        relations[name].append(constants.asList())
                else:
                    relations[name] = [constants.asList()]
                    print "Relation {} defined".format(name)


        except Exception as e:
            print "Exception: {}".format(e)

if __name__ == '__main__':
    shell()
