import pickle

from voteblockchain.block import Block
from voteblockchain.transaction import Coinbase, Transaction, TXInput, TXOutput
from voteblockchain.wallet import Wallet

wallets = []


class Blockchain:
    def __init__(self, address, mode="New"):
        if mode == "New":
            self.blocks = []
            transs = []
            transs.append(Coinbase(address))
            genesis_block = Block("", transs)
            genesis_block.set_hash()
            print(genesis_block.prev_block_hash)
            self.blocks.append(genesis_block)
            self.tx_about_to_add = []
        else:
            self.deserialize()

    def add_block(self, address):
        transs = []
        transs.append(Coinbase(address))
        prev_block = self.blocks[-1]
        new_block = Block(prev_block.hash, transs)
        new_block.set_hash()
        self.blocks.append(new_block)

    def mine_block(self):
        if len(self.tx_about_to_add) != 0:
            block = Block(self.blocks[-1].hash, self.tx_about_to_add.copy())
            block.set_hash()
            self.blocks.append(block)
        self.tx_about_to_add.clear()

    def find_unspent(self, address):
        unlockable_outputs = {}
        for i in self.blocks:  # по всем блокам в блокчейне
            for j in i.transactions:  # по всем транзакцям в каждом блоке
                tx_id = str(j.tx_id)
                for out in range(len(j.outputs)):  # по всем выходам из каждой транзакции
                    if "Coinbase" in str(type(j)):
                        if j.can_be_unlocked_with(out, address):  # найти выходы, которые принадлежат >address<
                            tx_id += "-" + str(out)
                            unlockable_outputs[tx_id] = j.outputs[out]
                    elif "Transaction" in str(type(j)):
                        if j.outputs[out].is_locked_with_key(address):
                            tx_id += "-" + str(out)
        out_keys = []
        tx_keys = []
        for key in unlockable_outputs.keys():  # составление списка идентификаторов для упрощения поиска ниже:
            k = key.split(sep="-")
            tx_keys.append(k[0])
            out_keys.append(k[-1])
        for i in self.blocks:  # по всем блокам в блокчейне
            for j in i.transactions:  # по всем транзакциям в каждом блоке
                for inp in j.inputs:  # по всем входам в каждой транзакции
                    if str(inp.tx_id) in tx_keys and str(inp.vout) in out_keys:  # ищем потраченные выходы
                        try:
                            unlockable_outputs.pop(str(inp.tx_id) + "-" + str(inp.vout))
                        except KeyError:
                            pass
        return unlockable_outputs

    def get_balance(self, address):
        balance = 0
        outs = self.find_unspent(address)
        for i in outs.values():
            balance += i.value
        return balance

    def new_transaction(self, from_, to_, amount):
        accumulated, spendable = self.find_spendable_outputs(from_, amount)
        ins = []
        for i in spendable:
            tx_id, vout = i[0], i[1]  # в spendable список кортежей (id транзакции, номер выхода)
            ins.append(TXInput(tx_id, vout, from_, None))
        outs = []
        outs.append(TXOutput(amount, to_))
        if accumulated > amount:
            outs.append(TXOutput(accumulated - amount, from_))  # сдача, если набрали с баланса больше, чем надо
        tx = Transaction(ins, outs)
        self.tx_about_to_add.append(tx)
        return tx

    def find_spendable_outputs(self, address, amount):
        outs = self.find_unspent(address)
        accumulated = 0
        spendable = []
        for key, val in outs.items():
            k = key.split(sep="-")
            if accumulated < amount:
                spendable.append(k)
                accumulated += val.value
            else:
                print(accumulated)
                print(spendable)
                break
        return accumulated, spendable

    def send(self, from_, to_, amount):
        try:
            self.new_transaction(from_, to_, amount)
        except Exception as e:
            print(e)
        self.mine_block()
        print("Success!")

    def create_wallet(self):
        global wallets
        w = Wallet()
        wallets.append(w)
        return w.generate_address()

    def serialize(self):
        with open("blockchain.txt", mode="wb") as f:
            pickle.dump(self, f)

    def deserialize(self):
        with open("blockchain.txt", mode="rb") as f:
            obj_data = pickle.load(f)
        self.blocks = obj_data.blocks
        pass


if __name__ == "__main__":

    w1 = Wallet()
    address_1 = w1.generate_address()
    print("Address_1 = " + str(address_1) + "\n")

    w2 = Wallet()
    address_2 = w2.generate_address()
    print("Address_2 = " + str(address_2) + "\n")

    bc = Blockchain(address_1)

    print("Balance 1: " + str(bc.get_balance(address_1)))

    bc.add_block(address_2)

    bc.send(address_1, address_2, 1)

    print("A1 balance: " + str(bc.get_balance(address_1)))

    print("A2 balance: " + str(bc.get_balance(address_2)))
    # bc.add_block("A")
    # bc.add_block("X")

    for i in bc.blocks:
        print("Prev. hash: " + str(i.prev_block_hash))
        # print("Data: " + str(i.transactions))
        print("Transactions: ")
        for j in i.transactions:
            print("----", j.tx_id)
            print("----", j.inputs)
            print("----", j.outputs)
        print("Hash: " + str(i.hash))
        print()
    bc.serialize()
