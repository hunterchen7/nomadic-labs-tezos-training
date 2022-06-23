import smartpy as sp

owner = sp.address('tz1NLhVSPAgF2JRksYvMAzs59n24c2gh7QoQ')
alice = sp.address('tz1KrEbjH8NS3ptA7YnhkS59Ln5Gij1SvJvf')
bob = sp.address('tz1g9Ym3Qj8BVhcEsuvGkohA2ij94vXJaDCa')

class VerifiedCounter(sp.Contract):
    def __init__(self):
        self.init(lastAdder = sp.address('tz1NLhVSPAgF2JRksYvMAzs59n24c2gh7QoQ'), counter = 0)

    @sp.entry_point
    def addNumber(self, number):
        sp.verify(sp.sender != self.data.lastAdder, 'last caller cannot add a new number')
        sp.verify(number > 0, 'number must be positive')
        sp.verify(number < 10, 'number must be less than 10')
        self.data.lastAdder = sp.sender
        self.data.counter += number 

    @sp.entry_point
    def subtractNumber(self, number):
        sp.verify(sp.sender == owner, 'only owner can subtract')
        self.data.counter -= number

    @sp.entry_point
    def reset(self):
        sp.verify(sp.sender == owner, 'only owner can reset')
        self.data.counter = 0

@sp.add_test(name = "VerifiedCounter")
def test():
    c1 = VerifiedCounter()
    scenario = sp.test_scenario()
    scenario += c1

    ''' 
    test cases: 
        addNumber:
            last caller calls -> doesn't work
            not last caller calls with negative number -> doesn't work
            not last caller calls with number between 0 and 10 -> works
            not last caller calls with number 10 or greater -> doesn't work
        subtract:
            owner calls -> works
            not owner calls -> doesn't work
        reset:
            owner calls -> works
            not owner calls -> doesn't work
    '''

    scenario += c1.addNumber(1).run(sender = bob)
    scenario.verify_equal(c1.data.counter, 1)
    scenario.verify_equal(c1.data.lastAdder, bob)

    scenario += c1.addNumber(1).run(sender = bob, valid=False) # last caller attempts to add, doesn't work
    scenario.verify_equal(c1.data.counter, 1)
    scenario.verify_equal(c1.data.lastAdder, bob)
  
    scenario += c1.addNumber(9).run(sender = owner)
    scenario.verify_equal(c1.data.counter, 10)
    scenario.verify_equal(c1.data.lastAdder, owner)

    scenario += c1.addNumber(2).run(sender = bob)
    scenario.verify_equal(c1.data.counter, 12)
    scenario.verify_equal(c1.data.lastAdder, bob)

    # non positive

    scenario += c1.addNumber(-1).run(sender = bob, valid=False) # non last caller calls with negative number, doesn't work
    scenario.verify_equal(c1.data.counter, 12)
    scenario.verify_equal(c1.data.lastAdder, bob) 

    scenario += c1.addNumber(0).run(sender = bob, valid=False) # non last caller calls with non-positive number, doesn't work
    scenario.verify_equal(c1.data.counter, 12)
    scenario.verify_equal(c1.data.lastAdder, bob) 

    scenario += c1.addNumber(0).run(sender = alice, valid=False) # non last caller calls with non-positive number, doesn't work
    scenario.verify_equal(c1.data.counter, 12)
    scenario.verify_equal(c1.data.lastAdder, bob) 

    scenario += c1.addNumber(-17).run(sender = bob, valid=False) # non last caller calls with negative number, doesn't work
    scenario.verify_equal(c1.data.counter, 12)
    scenario.verify_equal(c1.data.lastAdder, bob)

    # greater than or equal to 10

    scenario += c1.addNumber(10).run(sender = alice, valid=False) # last caller attempts to add a number 10 or greater, doesn't work
    scenario.verify_equal(c1.data.counter, 12)
    scenario.verify_equal(c1.data.lastAdder, bob)

    scenario += c1.addNumber(13).run(sender = owner, valid=False) # non last caller calls with number 10 or greater, doesn't work
    scenario.verify_equal(c1.data.counter, 12)
    scenario.verify_equal(c1.data.lastAdder, bob)

    scenario += c1.addNumber(58).run(sender = owner, valid=False) # non last caller calls with number 10 or greater, doesn't work
    scenario.verify_equal(c1.data.counter, 12)
    scenario.verify_equal(c1.data.lastAdder, bob) 

    # subtraction

    scenario += c1.subtractNumber(5).run(sender = owner) # owner calls subtract, works
    scenario.verify_equal(c1.data.counter, 7)
    scenario.verify_equal(c1.data.lastAdder, bob) # note that only addNumber changes last caller

    scenario += c1.subtractNumber(3).run(sender = bob, valid=False) # non owner can't call subtract, doesn't work
    scenario.verify_equal(c1.data.counter, 7)
    scenario.verify_equal(c1.data.lastAdder, bob)

    # reset
  
    scenario += c1.reset().run(sender = alice, valid=False) # non owner can't call reset, doesn't work
    scenario.verify_equal(c1.data.counter, 7)
    scenario.verify_equal(c1.data.lastAdder, bob)

    scenario += c1.reset().run(sender = owner) # owner calls reset, works
    scenario.verify_equal(c1.data.counter, 0)
    scenario.verify_equal(c1.data.lastAdder, bob)

    # random adding

    scenario += c1.addNumber(3).run(sender = owner)
    scenario.verify_equal(c1.data.counter, 3)
    scenario.verify_equal(c1.data.lastAdder, owner)
  
    scenario += c1.addNumber(3).run(sender = alice)
    scenario.verify_equal(c1.data.counter, 6)
    scenario.verify_equal(c1.data.lastAdder, alice)

    scenario += c1.addNumber(9).run(sender = bob)
    scenario.verify_equal(c1.data.counter, 15)
    scenario.verify_equal(c1.data.lastAdder, bob)

    scenario += c1.addNumber(6).run(sender = alice)
    scenario.verify_equal(c1.data.counter, 21)
    scenario.verify_equal(c1.data.lastAdder, alice)

    scenario += c1.addNumber(-3).run(sender = bob, valid=False) # non last caller calls with negative number, doesn't work
    scenario.verify_equal(c1.data.counter, 21)
    scenario.verify_equal(c1.data.lastAdder, alice)

    # random subtracting

    scenario += c1.subtractNumber(3).run(sender = owner)
    scenario.verify_equal(c1.data.counter, 18)
    scenario.verify_equal(c1.data.lastAdder, alice)

    scenario += c1.subtractNumber(3).run(sender = alice, valid=False) # non owner calls subtract, no changes
    scenario.verify_equal(c1.data.counter, 18)
    scenario.verify_equal(c1.data.lastAdder, alice)
