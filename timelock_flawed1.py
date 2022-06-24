import smartpy as sp

owner = sp.address("tz1KqTpEZ7Yob7QbPE4Hy4Wo8fHG8LhKxZSx")

class TimeLock(sp.Contract):
   def __init__(self, date):
      self.init(deadline = date)

   @sp.entry_point
   def deposit(self, newDeadline):
      sp.if (newDeadline > self.data.deadline):
         self.data.deadline = newDeadline

   @sp.entry_point
   def claim(self, requestedAmount):
      sp.verify(sp.now > self.data.deadline, "Too early") # check that the deadline has passed
      sp.verify(sp.sender == owner, "Access forbiden")
      amount = sp.local('amount', requestedAmount)
      sp.if (amount.value >= sp.balance):
         amount.value = sp.balance
      sp.send(sp.sender, amount.value)