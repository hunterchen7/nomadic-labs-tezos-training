import smartpy as sp

owner_ = sp.address('tz1NLhVSPAgF2JRksYvMAzs59n24c2gh7QoQ')
alice = sp.address('tz1KrEbjH8NS3ptA7YnhkS59Ln5Gij1SvJvf')
bob = sp.address('tz1g9Ym3Qj8BVhcEsuvGkohA2ij94vXJaDCa')

class NFT(sp.Contract):
  def __init__(self):
    self.init(
      nfts = {}
    )

  def generate_address(self):
    contract = sp.create_contract_operation(sp.Contract(), sp.unit, sp.tez(0), None)
    return contract.address

  @sp.entry_point
  def mint(self, metadata, price):
    tokenId = self.generate_address()
    sp.set_type(metadata, sp.TString)
    sp.set_type(price, sp.TMutez)
    self.data.nfts[tokenId] = sp.record(owner = sp.sender, metadata = metadata, price = price)
  
  @sp.entry_point
  def transfer(self, newOwner, tokenId):
    sp.verify(self.data.nfts[tokenId].owner == sp.sender, 'only the owner can transfer an NFT')
    sp.verify(newOwner != sp.sender, 'cannot transfer to self')
    self.data.nfts[tokenId].owner = newOwner

@sp.add_test(name='NFT')
def test():
  c1 = NFT()
  scenario = sp.test_scenario()
  scenario += c1
  
  c1.mint(metadata='metadata for nft 1', price=sp.tez(1)).run(sender = owner_)
  c1.mint(metadata='metadata for nft 2', price=sp.tez(1)).run(sender = owner_)
  c1.mint(metadata='metadata for nft 3 aoiwjefpoiajwopfijwef', price=sp.tez(1)).run(sender = owner_)
  c1.mint(metadata='metadata for nft 4', price=sp.tez(1)).run(sender = owner_)
  c1.mint(metadata='metadata for nft 5', price=sp.tez(1)).run(sender = owner_)
  c1.mint(metadata='metadata for nft 6', price=sp.tez(1)).run(sender = owner_)
  c1.mint(metadata='metadata for nft 7', price=sp.tez(1)).run(sender = owner_)
  c1.mint(metadata='metadata for nft 8', price=sp.tez(1)).run(sender = owner_)
  c1.mint(metadata='metadata for nft 9', price=sp.tez(1)).run(sender = owner_)