############################################################
# HOMEWORK 1
#
# Team members: Hannah Twigg-Smith, Philip Seger
#
# Emails: Hannah.Twigg-Smith@students.olin.edu, Philip.Seger@students.olin.edu
#
# Remarks:
#




#
# Expressions
#

class Exp(object):
    pass


class EInteger(Exp):
    # Integer literal

    def __init__(self, i):
        self._integer = i

    def __str__(self):
        return "EInteger({})".format(self._integer)

    def eval(self):
        return VInteger(self._integer)


class EBoolean(Exp):
    # Boolean literal

    def __init__(self, b):
        self._boolean = b

    def __str__(self):
        return "EBoolean({})".format(self._boolean)

    def eval(self):
        return VBoolean(self._boolean)


class EVector(Exp):
    # Vector literal

    def __init__(self, v):
        self._vector = v

    def __str__(self):
        return "EVector({})".format(self._vector)

    def eval(self):
        return VVector(self._vector)


class EDiv(Exp):
    # Rational operations

    def __init__(self, e1, e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__(self):
        return "EDiv({} / {})".format(self._exp1, self._exp2)

    def eval(self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()

        if v1.type == "rational":
            if v2.type == "rational":
                return EDiv(EInteger(ETimes(EInteger(v1.numer), EInteger(v2.denom)).eval().value),
                            EInteger(ETimes(EInteger(v2.numer), EInteger(v1.denom)).eval().value)).eval()
            else:
                return EDiv(EInteger(v1.numer),
                            EInteger(ETimes(EInteger(v2.value), EInteger(v1.denom)).eval().value)).eval()
        elif v1.type == "integer":
            if v2.type == "integer":
                return VRational(v1.value, v2.value)
            else:
                return EDiv(EInteger(ETimes(EInteger(v1.value), EInteger(v2.denom)).eval().value),
                            EInteger(v2.numer)).eval()
        return None


class EPlus(Exp):
    # Addition operation

    def __init__(self, e1, e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__(self):
        return "EPlus({},{})".format(self._exp1, self._exp2)

    def eval(self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "integer" and v2.type == "integer":
            return VInteger(v1.value + v2.value)
        elif v1.type == "vector" and v2.type == "vector":
            vector = []
            for i in range(v1.length):
                if v1.get(i).type == "integer" and v2.get(i).type == "integer":
                    vector.append(EPlus(EInteger(v1.get(i).value), EInteger(v2.get(i).value)))
            return VVector(vector)
        raise Exception("Runtime error: trying to add non-numbers")


class EMinus(Exp):
    # Subtraction operation

    def __init__(self, e1, e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__(self):
        return "EMinus({},{})".format(self._exp1, self._exp2)

    def eval(self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "integer" and v2.type == "integer":
            return VInteger(v1.value - v2.value)
        elif v1.type == "vector" and v2.type == "vector":
            vector = []
            for i in range(v1.length):
                if v1.get(i).type == "integer" and v2.get(i).type == "integer":
                    vector.append(EMinus(EInteger(v1.get(i).value), EInteger(v2.get(i).value)))
            return VVector(vector)
        raise Exception("Runtime error: trying to subtract non-numbers")


class ETimes(Exp):
    # Multiplication operation

    def __init__(self, e1, e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__(self):
        return "ETimes({},{})".format(self._exp1, self._exp2)

    def eval(self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()
        if v1.type == "integer" and v2.type == "integer":
            return VInteger(v1.value * v2.value)
        elif v1.type == "vector" and v2.type == "vector":
            vector = []
            for i in range(v1.length):
                if v1.get(i).type == "integer" and v2.get(i).type == "integer":
                    vector.append(ETimes(EInteger(v1.get(i).value), EInteger(v2.get(i).value)).eval().value)
            counter = 0
            for val in vector:
                counter += val
            return VInteger(counter)
        raise Exception("Runtime error: trying to multiply non-numbers")


class EIf(Exp):
    # Conditional expression

    def __init__(self, e1, e2, e3):
        self._cond = e1
        self._then = e2
        self._else = e3

    def __str__(self):
        return "EIf({},{},{})".format(self._cond, self._then, self._else)

    def eval(self):
        v = self._cond.eval()
        if v.type != "boolean":
            raise Exception("Runtime error: condition not a Boolean")
        if v.value:
            return self._then.eval()
        else:
            return self._else.eval()


class EIsZero(Exp):
    # IsZero operation/check

    def __init__(self, e1):
        self._exp1 = e1

    def __str__(self):
        return "EIsZero({})".format(self._exp1)

    def eval(self):
        v1 = self._exp1.eval()
        if v1.type == "integer":
            if v1.value == 0:
                return VBoolean(True)
            else:
                return VBoolean(False)
        raise Exception("Runtime error: value is not an integer")


class EAnd(Exp):
    # And operation

    def __init__(self, e1, e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__(self):
        return "EAnd({}, {})".format(self._exp1, self._exp2)

    def eval(self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()

        if v1.type == "vector" and v2.type == "vector":
            vector = []
            for i in range(v1.length):
                if v1.get(i).type == "boolean" and v2.get(i).type == "boolean":
                    vector.append(EAnd(EBoolean(v1.get(i).value), EBoolean(v2.get(i).value)))
            return VVector(vector)

        if not v1.value:
            return VBoolean(False)
        elif v1.value and v2.value:
            return VBoolean(True)
        else:
            return VBoolean(False)
            # TODO: should throw an exception if types fail above


class EOr(Exp):
    # Or operation

    def __init__(self, e1, e2):
        self._exp1 = e1
        self._exp2 = e2

    def __str__(self):
        return "EOr({}, {})".format(self._exp1, self._exp2)

    def eval(self):
        v1 = self._exp1.eval()
        v2 = self._exp2.eval()

        if v1.type == "vector" and v2.type == "vector":
            vector = []
            for i in range(v1.length):
                if v1.get(i).type == "boolean" and v2.get(i).type == "boolean":
                    vector.append(EOr(EBoolean(v1.get(i).value), EBoolean(v2.get(i).value)))
            return VVector(vector)

        if v1.value or v2.value:
            return VBoolean(True)
        else:
            return VBoolean(False)


class ENot(Exp):
    # Not operation

    def __init__(self, e):
        self._exp = e

    def __str__(self):
        return "ENot({})".format(self._exp1)

    def eval(self):
        v1 = self._exp.eval()

        if v1.type == "vector":
            vector = []
            for i in range(v1.length):
                if v1.get(i).type == "boolean":
                    vector.append(ENot(EBoolean(v1.get(i).value)))
            return VVector(vector)

        if not v1.value:
            return VBoolean(True)
        else:
            return VBoolean(False)


#
# Values
#

class Value(object):
    pass


class VInteger(Value):
    # Value representation of integers
    def __init__(self, i):
        self.value = i
        self.type = "integer"


class VBoolean(Value):
    # Value representation of Booleans
    def __init__(self, b):
        self.value = b
        self.type = "boolean"


class VVector(Value):
    # Value representation of Vectors
    def __init__(self, v):
        self.value = v
        self.length = len(v)
        self.type = "vector"

    def get(self, n):
        if n > self.length - 1 or n < 0:
            raise Exception("Not in bounds for vector")
        return self.value[n].eval()


class VRational(Value):
    # Value representation of Rationals
    def __init__(self, numer, denom):
        self.numer = numer
        self.denom = denom
        self.type = "rational"


#
# Testing code
#

if __name__ == '__main__':
    # EIsZero tests
    # print EIsZero(EInteger(0)).eval().value
    # print EIsZero(EInteger(1)).eval().value
    # print EIsZero(EInteger(9)).eval().value
    # print EIsZero(EInteger(-1)).eval().value
    # print EIsZero(EPlus(EInteger(1),EInteger(1))).eval().value
    # print EIsZero(EMinus(EInteger(1),EInteger(1))).eval().value

    # EAnd, EOr, ENot tests
    # tt = EBoolean(True)
    # ff = EBoolean(False)
    # print EAnd(tt, tt).eval().value
    # print EAnd(tt,ff).eval().value
    # print EAnd(ff,tt).eval().value
    # print EAnd(ff,ff).eval().value
    # print EOr(tt,tt).eval().value
    # print EOr(tt,ff).eval().value
    # print EOr(ff,tt).eval().value
    # print EOr(ff,ff).eval().value
    # print ENot(tt).eval().value
    # print ENot(ff).eval().value
    # print EAnd(EOr(tt,ff),EOr(ff,tt)).eval().value
    # print EAnd(EOr(tt,ff),EOr(ff,ff)).eval().value
    # print EAnd(tt,ENot(tt)).eval().value
    # print EAnd(tt,ENot(ENot(tt))).eval().value

    # EAnd, EOr, ENot short-circuit tests
    # tt = EBoolean(True)
    # ff = EBoolean(False)
    # print EAnd(ff,EInteger(10)).eval().value
    # print EAnd(ff,EInteger(0)).eval().value
    # print EOr(tt,EInteger(10)).eval().value
    # print EOr(tt,EInteger(0)).eval().value

    # VVector tests
    # print VVector([]).length
    # print VVector([VInteger(10),VInteger(20),VInteger(30)]).length
    # print VVector([VInteger(10),VInteger(20),VInteger(30)]).get(0).value
    # print VVector([VInteger(10),VInteger(20),VInteger(30)]).get(1).value
    # print VVector([VInteger(10),VInteger(20),VInteger(30)]).get(2).value

    # EVector tests
    # print EVector([]).eval().length
    # print EVector([EInteger(10),EInteger(20),EInteger(30)]).eval().length
    # print EVector([EInteger(10),EInteger(20),EInteger(30)]).eval().get(0).value
    # print EVector([EInteger(10),EInteger(20),EInteger(30)]).eval().get(1).value
    # print EVector([EInteger(10),EInteger(20),EInteger(30)]).eval().get(2).value
    # print EVector([EPlus(EInteger(1),EInteger(2)),EInteger(0)]).eval().length
    # print EVector([EPlus(EInteger(1),EInteger(2)),EInteger(0)]).eval().get(0).value
    # print EVector([EPlus(EInteger(1),EInteger(2)),EInteger(0)]).eval().get(1).value
    # print EVector([EBoolean(True),EAnd(EBoolean(True),EBoolean(False))]).eval().length
    # print EVector([EBoolean(True),EAnd(EBoolean(True),EBoolean(False))]).eval().get(0).value
    # print EVector([EBoolean(True),EAnd(EBoolean(True),EBoolean(False))]).eval().get(1).value

    # EPlus, EMinus, EOr, ENot with vectors
    # def pair (v): return (v.get(0).value,v.get(1).value)
    # v1 = EVector([EInteger(2),EInteger(3)])
    # v2 = EVector([EInteger(33),EInteger(66)])
    # print pair(EPlus(v1,v2).eval())
    # print pair(EMinus(v1,v2).eval())
    # b1 = EVector([EBoolean(True),EBoolean(False)])
    # b2 = EVector([EBoolean(False),EBoolean(False)])
    # print pair(EAnd(b1,b2).eval())
    # print pair(EOr(b1,b2).eval())
    # print pair(ENot(b1).eval())

    # ETimes with vectors
    # v1 = EVector([EInteger(2), EInteger(3)])
    # v2 = EVector([EInteger(33), EInteger(66)])
    # print ETimes(v1, v2).eval().value
    # print ETimes(v1, EPlus(v2, v2)).eval().value
    # print ETimes(v1, EMinus(v2, v2)).eval().value

    # VRational tests
    # print VRational(1, 3).numer
    # print VRational(1, 3).denom
    # print VRational(2, 3).numer
    # print VRational(2, 3).denom

    # EDiv tests
    def rat(v): return "{}/{}".format(v.numer, v.denom)
    print rat(EDiv(EInteger(1), EInteger(2)).eval())
    print rat(EDiv(EInteger(2), EInteger(3)).eval())
    print rat(EDiv(EDiv(EInteger(2), EInteger(3)), EInteger(4)).eval())
    print rat(EDiv(EInteger(2), EDiv(EInteger(3), EInteger(4))).eval())
