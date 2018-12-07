import pickle

from voteblockchain.wallet import Wallet


class Wallets:
    def __init__(self):
        self.wallets = {}

    def create_wallet(self):
        w = Wallet()
        address = w.generate_address()
        self.wallets[address] = w
        self.serialize()
        return address

    def get_addresses(self):
        addresses = []
        for address in self.wallets.keys():
            addresses.append(address)
        return addresses

    def get_wallet(self, address):
        return self.wallets[address]

    def serialize(self):
        with open("wallets.txt", mode="wb") as f:
            pickle.dump(self, f)


def deserialize():
    with open("wallets.txt", mode="rb") as f:
        w = Wallets()
        w_from_file = pickle.load(f)
        w = w_from_file
    return w
