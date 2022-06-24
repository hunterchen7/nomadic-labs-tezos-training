import smartpy as sp

class Escrow(sp.Contract):
    def __init__(self, seller, buyer, price):
        self.init(seller = seller, buyer = buyer, price = price, paid = False, confirmed = False)

    @sp.entry_point
    def pay(self): # buy calls to pay seller
        sp.verify(sp.sender == self.data.buyer, "Not the buyer")
        sp.verify(sp.amount == self.data.price, "Not the right price")
        sp.verify(~self.data.paid, "Already paid!")
        self.data.paid = True

    @sp.entry_point # if buyer refuses to confirm then seller loses money, so add some deposit
    def confirm(self): # buyer calls when they receive item
        sp.verify(sp.sender == self.data.buyer, "Not the buyer")
        sp.verify(self.data.paid, "Not paid")
        sp.verify(~self.data.confirmed, "Already confirmed")
        self.data.confirmed = True

    @sp.entry_point
    def claim(self): # seller calls when buyer confirms receiving
        sp.verify(sp.sender == self.data.seller, "Not the seller")
        sp.verify(self.data.confirmed, "Not confirmed")
        sp.send(sp.sender, sp.balance) # should send self.data.price instead?