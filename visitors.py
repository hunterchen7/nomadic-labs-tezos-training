import smartpy as sp

owner = sp.address('tz1NLhVSPAgF2JRksYvMAzs59n24c2gh7QoQ')
alice = sp.address('tz1KrEbjH8NS3ptA7YnhkS59Ln5Gij1SvJvf')
bob = sp.address('tz1g9Ym3Qj8BVhcEsuvGkohA2ij94vXJaDCa')

class Visitors(sp.Contract):
    def __init__(self):
        self.init(
          visitors = {}
        )

    @sp.entry_point
    def register(self, login, name):
      sp.set_type(name, sp.TString)
      sp.set_type(login, sp.TAddress)
      sp.verify(~self.data.visitors.contains(login), 'login already exists')
      self.data.visitors[login] = sp.record(visits = 0, name = name, lastVisit = sp.timestamp(0))

    @sp.entry_point
    def visit(self, login):
      sp.verify(self.data.visitors.contains(login), 'login not found')
      sp.verify(sp.now >= self.data.visitors[login].lastVisit.add_days(10), 'must wait 10 days between visits')
      sp.if self.data.visitors[login].visits == 0:
        sp.verify(sp.amount == sp.tez(5), 'must pay 5 tez for first visit')
      sp.else:
        sp.verify(sp.amount == sp.tez(3), 'must pay 3 tez for subsequent visits')
      self.data.visitors[login].visits += 1
      self.data.visitors[login].lastVisit = sp.now


@sp.add_test(name = "Visitors")
def test():
  c1 = Visitors()
  scenario = sp.test_scenario()
  scenario += c1

  c1.register(login = alice, name = 'Alice').run(sender = alice)
  scenario.verify_equal(c1.data.visitors[alice].name, 'Alice')
  scenario.verify_equal(c1.data.visitors[alice].visits, 0)
  c1.visit(alice).run(sender = alice, amount = sp.tez(0), valid=False, exception = 'must pay 5 tez for first visit', now=sp.now.add_days(10))
  scenario.verify_equal(c1.data.visitors[alice].visits, 0)
  c1.visit(alice).run(sender = alice, amount = sp.tez(5), now=sp.now.add_days(10))
  scenario.verify_equal(c1.data.visitors[alice].visits, 1)
  c1.visit(alice).run(sender = alice, amount = sp.tez(3), valid=False, exception = 'must wait 10 days between visits')
  scenario.verify_equal(c1.data.visitors[alice].visits, 1)
  c1.visit(alice).run(sender = alice, amount = sp.tez(3), now=sp.now.add_days(10))
  scenario.verify_equal(c1.data.visitors[alice].visits, 2)
  c1.visit(alice).run(sender = alice, amount = sp.tez(3), now=sp.now.add_days(9).add_hours(23).add_minutes(59).add_seconds(59), valid=False, exception = 'must wait 10 days between visits')
  scenario.verify_equal(c1.data.visitors[alice].visits, 2)
  c1.visit(alice).run(sender = alice, amount = sp.tez(3), now=sp.now.add_days(100))
  scenario.verify_equal(c1.data.visitors[alice].visits, 3)
  c1.visit(alice).run(sender = alice, amount = sp.tez(4), now=sp.now.add_days(100), valid=False, exception = 'must pay 3 tez for subsequent visits')
  scenario.verify_equal(c1.data.visitors[alice].visits, 3) 
  c1.visit(alice).run(sender = alice, amount = sp.tez(5), now=sp.now.add_days(100), valid=False, exception = 'must pay 3 tez for subsequent visits')
  scenario.verify_equal(c1.data.visitors[alice].visits, 3) 
  c1.visit(alice).run(sender = alice, amount = sp.tez(2), now=sp.now.add_days(100), valid=False, exception = 'must pay 3 tez for subsequent visits')
  scenario.verify_equal(c1.data.visitors[alice].visits, 3)

  c1.register(login = alice, name = "aLiCe").run(sender = alice, valid=False, exception = 'login already exists')

  c1.visit(bob).run(sender = bob, amount = sp.tez(5), valid=False, exception = 'login not found')
  c1.register(login = bob, name = 'Bob').run(sender = bob)
  c1.visit(bob).run(sender = bob, amount = sp.tez(5))
  scenario.verify_equal(c1.data.visitors[bob].visits, 1)
  c1.visit(bob).run(sender = bob, amount = sp.tez(3), valid=False, exception = 'must wait 10 days between visits')
  scenario.verify_equal(c1.data.visitors[bob].visits, 1)
  c1.visit(bob).run(sender = bob, amount = sp.tez(3), now=sp.now.add_days(10))
  scenario.verify_equal(c1.data.visitors[bob].visits, 2)
  c1.visit(alice).run(sender = alice, amount = sp.tez(3), now=sp.now.add_seconds(3727)) # works without adding 10 days because alice hasn't visited in a while
  scenario.verify_equal(c1.data.visitors[alice].visits, 4)
  c1.visit(alice).run(sender = alice, amount = sp.tez(3), now=sp.now.add_days(10))
  scenario.verify_equal(c1.data.visitors[alice].visits, 5)
  c1.visit(bob).run(sender = bob, amount = sp.tez(3))
  scenario.verify_equal(c1.data.visitors[bob].visits, 3)
  scenario.verify_equal(c1.data.visitors[alice].visits, 5)

  