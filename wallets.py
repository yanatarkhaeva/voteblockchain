import pickle

from wallet import Wallet


class Wallets:
    def __init__(self):
        self.wallets = {}

    def create_wallet(self):
        w = Wallet()
        address = w.generate_address()
        self.wallets[address] = w
        self.serialize()
        print(address)
        return address

    def get_addresses(self):
        addresses = []
        for address in self.wallets.keys():
            addresses.append(address)
        return addresses

    def get_wallet_by_pub_key(self, pub_key):
        for w in self.wallets.values():
            if w.public == pub_key:
                print(w.generate_address())
                return w.generate_address()

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
