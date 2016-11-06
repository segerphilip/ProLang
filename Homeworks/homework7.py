############################################################
# HOMEWORK 7
#
# Team members: Hannah Twigg-Smith, Philip Seger
#
# Emails: Hannah.Twigg-Smith@students.olin.edu, Philip.Seger@students.olin.edu
#
# Remarks:
#
############################################################
# Requirements:
# 
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


# 
# Expressions
# 
class Exp (object):
    pass


# 
# Values
# 
class Value (object):
    pass


# 
# Statements/functions?
# 
class Statement (object):
    pass


# 
# Parser
# 


def execute(filename):
    pass
