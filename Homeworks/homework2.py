############################################################
# HOMEWORK 2
#
# Team members: Hannah Twigg-Smith, Philip Seger
#
# Emails: Hannah.Twigg-Smith@students.olin.edu, Philip.Seger@students.olin.edu
#
# Remarks:
# We spent about 8 hours on this assignment, but we were unable to complete a
# fully functional version of ELetS. Our approach to ELetS involves recursing
# through the given expression to find blocking bindings, but we think that
# somewhere along the way we are doing something wrong, and we can't figure out
# where. Deniz Celik helped us understand some higher level concepts, and we
# think we know what is going on conceptually but are getting tripped up in the
# implementation. We also believe that we have the start of the implementation
# of ECall, but we don't know where we are supposed to call the substitute
# method and we've run out of time.

#
# Expressions
#

class Exp (object):
    pass



class EInteger (Exp):
    # Integer literal

    def __init__ (self,i):
        self._integer = i

    def __str__ (self):
        return "EInteger({})".format(self._integer)

    def eval (self,prim_dict):
        return VInteger(self._integer)

    def substitute (self,id,new_e):
        return self


class EBoolean (Exp):
    # Boolean literal

    def __init__ (self,b):
        self._boolean = b

    def __str__ (self):
        return "EBoolean({})".format(self._boolean)

    def eval (self,prim_dict):
        return VBoolean(self._boolean)

    def substitute (self,id,new_e):
        return self


class EPrimCall (Exp):

    def __init__ (self,name,es):
        self._name = name
        self._exps = es

    def __str__ (self):
        return "EPrimCall({},[{}])".format(self._name,",".join([ str(e) for e in self._exps]))

    def eval (self,prim_dict):
        vs = [ e.eval(prim_dict) for e in self._exps ]
        return apply(prim_dict[self._name],vs)

    def substitute (self,id,new_e):
        new_es = [ e.substitute(id,new_e) for e in self._exps]
        return EPrimCall(self._name,new_es)


class EIf (Exp):
    # Conditional expression

    def __init__ (self,e1,e2,e3):
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__ (self):
        return "EIf({},{},{})".format(self._cond,self._then,self._else)

    def eval (self,prim_dict):
        v = self._cond.eval(prim_dict)
        if v.type != "boolean":
            raise Exception ("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval(prim_dict)
        else:
            return self._else.eval(prim_dict)

    def substitute (self,id,new_e):
        return EIf(self._cond.substitute(id,new_e),
                   self._then.substitute(id,new_e),
                   self._else.substitute(id,new_e))


class ELet (Exp):
    # local binding

    def __init__ (self, bind_list, exp):
        self._bindings = bind_list
        self._exp = exp

    def __str__ (self):
        return "ELet({},{})".format(self._bindings, self._exp)

    def eval (self,prim_dict):
        newA = self._exp
        for x in self._bindings:
            newA = newA.substitute(x[0], x[1])
        print

        return newA.eval(prim_dict)

    def substitute (self,id,new_e):
        arr = []
        for binding in self._bindings:
            arr.append((binding[0], binding[1].substitute(id, new_e)))

        return ELet(arr, self._exp)


class ELetS (Exp):
    # local binding

    def __init__ (self, bind_list, exp):
        self._bindings = bind_list
        self._exp = exp

    def __str__ (self):
        return "ELet({},{})".format(self._bindings, self._exp)

    def eval (self,prim_dict):
        newA = self._exp
        for x in self._bindings:
            newA = newA.substitute(x[0], x[1])
        print

        return newA.eval(prim_dict)

    def substitute (self, id, new_e):
        print self._bindings
        bindings = self._bindings

        for index, binding in enumerate(bindings):
            if id == binding[0]:
                return ELet(bindings, new_e)
            bindings[index] = (bindings[index][0],bindings[index][1].substitute(id,new_e))

        return ELetS(bindings, self._exp)


class ELetV (Exp):
    # local binding

    def __init__ (self, id, e1, e2):
        self._id = id
        self._e1 = e1
        self._e2 = e2

    def __str__ (self):
        return "ELet({},{},{})".format(self._id, self._e1, self._e2)

    def eval (self,prim_dict):
        v = self._e1.eval(prim_dict)
        if v.type == "integer":
            new_e2 = self._e2.substitute(self._id, EInteger(v.value))

        return new_e2.eval(prim_dict)

    def substitute (self,id,new_e):
        if id == self._id:
            return ELetV(self._id,
                        self._e1.substitute(id,new_e),
                        self._e2)
        return ELetV(self._id,
                    self._e1.substitute(id,new_e),
                    self._e2.substitute(id,new_e))


class EId (Exp):
    # identifier

    def __init__ (self,id):
        self._id = id

    def __str__ (self):
        return "EId({})".format(self._id)

    def eval (self,prim_dict):
        raise Exception("Runtime error: unknown identifier {}".format(self._id))

    def substitute (self,id,new_e):
        if id == self._id:
            return new_e
        return self


class ECall (Exp):
    # expression node

    def __init__ (self, name, es):
        self._name = name
        self._exps = es

    def __str__ (self):
        return "EPrimCall({},[{}])".format(self._name,",".join([ str(e) for e in self._exps]))

    def eval (self, prim_dict, fun_dict):
        bindings = []
        for index, id in enumerate(self._exps):
            bindings.append((fun_dict[self._name]["params"][index],id))

        return ELet(bindings, fun_dict[self._name]["body"]).eval(prim_dict)

    def substitute (self, id, new_e):
        new_es = [e.substitute(id,new_e) for e in self._exps]
        return ECall(self._name, new_es)



class EValue (Exp):
    # value operator

    def __init__ (self,val):
        self._val = val

    def __str__ (self):
        return "EValue({})".format(self._val)

    def eval (self, prim_dict):
        return self._val

    def substitute (self, id, new_e):
        return self


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

class VBoolean (Value):
    # Value representation of Booleans
    def __init__ (self,b):
        self.value = b
        self.type = "boolean"



# Primitive operations

def oper_plus (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value + v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_minus (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value - v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_times (v1,v2):
    if v1.type == "integer" and v2.type == "integer":
        return VInteger(v1.value * v2.value)
    raise Exception ("Runtime error: trying to add non-numbers")

def oper_zero (v1):
   if v1.type == "integer":
       return VBoolean(v1.value==0)
   raise Exception ("Runtime error: type error in zero?")

# Initial primitives dictionary

INITIAL_PRIM_DICT = {
    "+": oper_plus,
    "*": oper_times,
    "-": oper_minus,
    "zero?": oper_zero
}

# Function dictionary
FUN_DICT = {
  "square": {"params":["x"],
             "body":EPrimCall("*",[EId("x"),EId("x")])},
  "=": {"params":["x","y"],
        "body":EPrimCall("zero?",[EPrimCall("-",[EId("x"),EId("y")])])},
  "+1": {"params":["x"],
         "body":EPrimCall("+",[EId("x"),EValue(VInteger(1))])},
  "sum_from_to": {"params":["s","e"],
                  "body":EIf(ECall("=",[EId("s"),EId("e")]),
                             EId("s"),
                             EPrimCall("+",[EId("s"),
                                            ECall("sum_from_to",[ECall("+1",[EId("s")]),
                                                                 EId("e")])]))}
}

#
# Testing code
#

if __name__ == '__main__':
    # ELet
    # print ELet([("a",EInteger(99))],EId("a")).eval(INITIAL_PRIM_DICT).value
    # print ELet([("a",EInteger(99)), ("b",EInteger(66))],EId("a")).eval(INITIAL_PRIM_DICT).value
    # print ELet([("a",EInteger(99)), ("b",EInteger(66))],EId("b")).eval(INITIAL_PRIM_DICT).value
    # print ELet([("a",EInteger(99))], ELet([("a",EInteger(66)), ("b", EId("a"))], EId("a"))).eval(INITIAL_PRIM_DICT).value
    # print ELet([("a",EInteger(99))], ELet([("a",EInteger(66)), ("b", EId("a"))], EId("b"))).eval(INITIAL_PRIM_DICT).value
    # print ELet([("a",EInteger(5)), ("b",EInteger(20))], ELet([("a",EId("b")), ("b",EId("a"))], EPrimCall("-",[EId("a"),EId("b")]))).eval(INITIAL_PRIM_DICT).value

    # ELetS
    # print ELetS([("a",EInteger(99))],EId("a")).eval(INITIAL_PRIM_DICT).value
    # print ELetS([("a",EInteger(99)),("b",EInteger(66))],EId("a")).eval(INITIAL_PRIM_DICT).value
    # print ELetS([("a",EInteger(99)),("b",EInteger(66))],EId("b")).eval(INITIAL_PRIM_DICT).value
    # print ELet([("a",EInteger(99))],ELetS([("a",EInteger(66)),("b",EId("a"))],EId("a"))).eval(INITIAL_PRIM_DICT).value
    # print ELet([("a",EInteger(99))],ELetS([("a",EInteger(66)),("b",EId("a"))],EId("b"))).eval(INITIAL_PRIM_DICT).value
    # print ELetS([("a",EInteger(5)),("b",EInteger(20))],ELetS([("a",EId("b")),("b",EId("a"))],EPrimCall("-",[EId("a"),EId("b")]))).eval(INITIAL_PRIM_DICT).value

    # ELetV
    # print ELetV("a",EInteger(10),EId("a")).eval(INITIAL_PRIM_DICT).value
    # print ELetV("a",EInteger(10),ELetV("b",EInteger(20),EId("a"))).eval(INITIAL_PRIM_DICT).value
    # print ELetV("a",EInteger(10),ELetV("a",EInteger(20),EId("a"))).eval(INITIAL_PRIM_DICT).value
    # print ELetV("a",EPrimCall("+",[EInteger(10),EInteger(20)]),ELetV("b",EInteger(20),EId("a"))).eval(INITIAL_PRIM_DICT).value
    # print ELetV("a",EPrimCall("+",[EInteger(10),EInteger(20)]),ELetV("b",EInteger(20),EPrimCall("*",[EId("a"),EId("a")]))).eval(INITIAL_PRIM_DICT).value

    # ECall
    # print ECall("+1",[EInteger(100)]).eval(INITIAL_PRIM_DICT,FUN_DICT).value
    # print ECall("+1",[EPrimCall("+",[EInteger(100),EInteger(200)])]).eval(INITIAL_PRIM_DICT,FUN_DICT).value
    # print ECall("+1",[ECall("+1",[EInteger(100)])]).eval(INITIAL_PRIM_DICT,FUN_DICT).value
    # print ECall("=",[EInteger(1),EInteger(2)]).eval(INITIAL_PRIM_DICT,FUN_DICT).value
    # print ECall("=",[EInteger(1),EInteger(1)]).eval(INITIAL_PRIM_DICT,FUN_DICT).value
    # print ECall("sum_from_to",[EInteger(0),EInteger(10)]).eval(INITIAL_PRIM_DICT,FUN_DICT).value
