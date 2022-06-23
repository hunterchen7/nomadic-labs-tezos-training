import smartpy as sp

owner = sp.address('tz1NLhVSPAgF2JRksYvMAzs59n24c2gh7QoQ')
alice = sp.address('tz1KrEbjH8NS3ptA7YnhkS59Ln5Gij1SvJvf')
bob = sp.address('tz1g9Ym3Qj8BVhcEsuvGkohA2ij94vXJaDCa')

class Transactions(sp.Contract):
  def __init__(self):
    self.init(lastWithdrawlTime = sp.timestamp(0), maxWithdrawalPercent = 100)

  @sp.entry_point
  def collect(self, amount):
    sp.verify(sp.sender == owner, 'only the owner can collect')
    sp.verify(sp.now >= self.data.lastWithdrawlTime.add_minutes(2), 'must wait 2 minutes between withdrawals')
    sp.verify(amount <= sp.balance, 'amount must be less than or equal to balance')
    sp.verify(amount <= sp.split_tokens(sp.balance, self.data.maxWithdrawalPercent, 100), 'amount must be less than or equal to max withdrawal amount')
    self.data.lastWithdrawlTime = sp.now
    sp.send(owner, amount)
    
  @sp.entry_point
  def deposit(self, newMaxWithdrawalPercent):
    sp.if sp.amount >= sp.tez(100):
      sp.if newMaxWithdrawalPercent != sp.none:
        sp.verify(newMaxWithdrawalPercent.open_some() >= 1, 'max withdrawal percentage must be greater than or equal to 1%')
        sp.verify(newMaxWithdrawalPercent.open_some() <= 100, 'max withdrawal percentage cannot exceed 100%')
        self.data.maxWithdrawalPercent = newMaxWithdrawalPercent.open_some()

@sp.add_test(name = "Transactions")
def test():
  c1 = Transactions()
  scenario = sp.test_scenario()
  scenario += c1

  scenario += c1.deposit(sp.none).run(sender = alice, amount = sp.tez(1000))

  # test non-owner withdrawl
  scenario += c1.collect(sp.tez(100)).run(sender = bob, now = sp.now.add_minutes(5), valid=False)
  scenario += c1.collect(sp.tez(100)).run(sender = alice, now = sp.now.add_minutes(5), valid=False)
  scenario.verify_equal(c1.balance, sp.tez(1000))

  # test withdrawing at different times
  
  # just under 2 minutes
  scenario += c1.collect(sp.tez(100)).run(sender = owner, now = sp.now.add_minutes(1), valid=False)
  scenario.verify_equal(c1.balance, sp.tez(1000))
  scenario += c1.collect(sp.tez(100)).run(sender = owner, now = sp.now.add_seconds(119), valid=False)
  scenario.verify_equal(c1.balance, sp.tez(1000))

  # 2 minutes exactly
  scenario += c1.collect(sp.tez(100)).run(sender = owner, now = sp.now.add_minutes(2))
  scenario.verify_equal(c1.balance, sp.tez(900))

  # under 2 minutes
  scenario += c1.collect(sp.tez(100)).run(sender = owner, now = sp.now.add_minutes(1), valid=False)
  scenario += c1.collect(sp.tez(100)).run(sender = owner, now = sp.now.add_seconds(119), valid=False)
  scenario += c1.collect(sp.tez(100)).run(sender = owner, now = sp.now.add_seconds(4), valid=False)
  scenario.verify_equal(c1.balance, sp.tez(900))

  # 2 minutes or over
  scenario += c1.collect(sp.tez(100)).run(sender = owner, now = sp.now.add_seconds(120))
  scenario += c1.collect(sp.tez(100)).run(sender = owner, now = sp.now.add_seconds(121))
  scenario += c1.collect(sp.tez(100)).run(sender = owner, now = sp.now.add_minutes(12))
  scenario += c1.collect(sp.tez(100)).run(sender = owner, now = sp.now.add_hours(3))
  scenario += c1.collect(sp.tez(100)).run(sender = owner, now = sp.now.add_days(4))
  scenario.verify_equal(c1.balance, sp.tez(400))

  # test max withdrawal amount

  # testing available balance  
  scenario += c1.collect(sp.tez(4000999)).run(sender = owner, now = sp.now.add_minutes(2), valid=False)
  scenario += c1.collect(sp.tez(401)).run(sender = owner, now = sp.now.add_minutes(2), valid=False)
  scenario += c1.collect(sp.tez(400)).run(sender = owner, now = sp.now.add_minutes(2))
  scenario.verify_equal(c1.balance, sp.tez(0))

  # testing changing max withdrawal amount
  scenario += c1.deposit(sp.some(90)).run(sender = bob, amount = sp.tez(10000))
  scenario += c1.deposit(sp.some(100)).run(sender = bob, amount = sp.tez(99)) # deposit less than 100
  scenario.verify_equal(c1.data.maxWithdrawalPercent, 90)
  scenario += c1.deposit(sp.some(432)).run(sender = bob, amount = sp.tez(100), valid=False)
  scenario += c1.deposit(sp.none).run(sender = bob, amount = sp.tez(100))
  scenario.verify_equal(c1.data.maxWithdrawalPercent, 90)
  scenario += c1.deposit(sp.some(1)).run(sender = alice, amount = sp.tez(1000))
  scenario += c1.deposit(sp.some(0)).run(sender = bob, amount = sp.tez(1000), valid=False)
  scenario.verify_equal(c1.data.maxWithdrawalPercent, 1)

  # testing max withdrawal amount
  scenario += c1.deposit(sp.some(10)).run(sender = bob, amount = sp.tez(88801)) # exactly 100k tezos
  scenario += c1.collect(sp.tez(10001)).run(sender = owner, now = sp.now.add_minutes(2), valid=False) # slightly more than 10%
  scenario += c1.collect(sp.tez(10000)).run(sender = owner, now = sp.now.add_minutes(2)) # exactly 10%
  scenario.verify_equal(c1.balance, sp.tez(90000))
  scenario += c1.deposit(sp.none).run(sender = alice, amount = sp.tez(10000)) # top up back to 100k
  scenario.verify_equal(c1.balance, sp.tez(100000))
  scenario += c1.collect(sp.tez(5000)).run(sender = owner, now = sp.now.add_minutes(2))
  scenario.verify_equal(c1.balance, sp.tez(95000))
  scenario += c1.collect(sp.tez(30000)).run(sender = owner, now = sp.now.add_minutes(2), valid=False)