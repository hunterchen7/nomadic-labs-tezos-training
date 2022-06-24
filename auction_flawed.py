import smartpy as sp

class Auction(sp.Contract):
  def __init__(self, owner, deadline):
    self.init(owner = owner, deadline = deadline, topBidder = owner,
      bids = { owner: sp.tez(0) })

  @sp.entry_point
  def bid(self):
    sp.verify(sp.now < self.data.deadline, "Too late!")
    bids = self.data.bids
    sp.verify(~bids.contains(sp.sender), "You already bid")
    bids[sp.sender] = sp.amount
    sp.if sp.amount > bids[self.data.topBidder]:
      self.data.topBidder = sp.sender

  @sp.entry_point
  def collectTopBid(self):
    sp.verify(sp.now >= self.data.deadline, "Too early!")
    sp.verify(sp.sender == self.data.owner)
    sp.send(sp.sender, self.data.bids[self.data.topBidder])
  
  @sp.entry_point
  def claim(self):
    sp.verify(self.data.bids.contains(sp.sender))
    sp.verify(sp.now >= self.data.deadline, "To early!")
    sp.verify(sp.sender != self.data.topBidder, "You won the auction")
    sp.send(sp.sender, self.data.bids[sp.sender])

@sp.add_test(name = "Auction")
def test():
  start = sp.timestamp_from_utc_now()
  stop = start.add_minutes(10)
  later = start.add_minutes(20)
  alice = sp.test_account("Alice").address
  bob = sp.test_account("Bob").address
  carl = sp.test_account("Carl").address
  c1 = Auction(owner = alice, deadline = stop)
  scenario = sp.test_scenario()
  scenario.h1("Auction")
  scenario += c1
  scenario += c1.bid().run(now = start, sender = bob, amount = sp.tez(10))
  scenario += c1.bid().run(now = start, sender = carl, amount = sp.tez(15))
  scenario += c1.collectTopBid().run(now = later, sender = alice)
  scenario += c1.claim().run(now = later, sender = bob)