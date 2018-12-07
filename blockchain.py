import pickle

import voteblockchain.wallets as Ws
from voteblockchain.block import Block
from voteblockchain.transaction import Coinbase, Transaction, TXInput, TXOutput
from voteblockchain.wallet import Wallet

wallets = []


class Blockchain:
    def __init__(self, address, mode="New"):
        if mode == "New":
            self.blocks = []
            transs = []
            c = Coinbase(address)
            c.set_id()
            transs.append(c)
            genesis_block = Block("", transs)
            genesis_block.set_hash()
            print(genesis_block.prev_block_hash)
            self.blocks.append(genesis_block)
            self.tx_about_to_add = []
        else:
            self.deserialize()

    def add_block(self, address):
        transs = []
        c = Coinbase(address)
        c.set_id()
        transs.append(c)
        prev_block = self.blocks[-1]
        new_block = Block(prev_block.hash, transs)
        new_block.set_hash()
        self.blocks.append(new_block)

    def mine_block(self):
        if len(self.tx_about_to_add) != 0:
            txxs = []
            for tx in self.tx_about_to_add:
                if self.verify_transaction(tx):
                    txxs.append(tx)
            if len(txxs) != 0:
                block = Block(self.blocks[-1].hash, txxs)
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
        ws = Ws.deserialize()
        wallet = ws.get_wallet(from_)
        for i in spendable:
            tx_id, vout = i[0], i[1]  # в spendable список кортежей (id транзакции, номер выхода)
            ins.append(TXInput(tx_id, vout, from_, wallet.public))
        outs = []
        outs.append(TXOutput(amount, to_))
        if accumulated > amount:
            outs.append(TXOutput(accumulated - amount, from_))  # сдача, если набрали с баланса больше, чем надо
        tx = Transaction(ins, outs)
        tx.set_id()
        # tx.tx_id = tx.hashhash()
        self.sing_transaction(tx, wallet.private)
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
        self.new_transaction(from_, to_, amount)
        # except Exception as e:
        #     print(e)
        self.mine_block()
        print("Success!")

    def create_wallet(self):
        global wallets
        w = Wallet()
        wallets.append(w)
        return w.generate_address()

    def find_transaction(self, transaction):
        for b in self.blocks:
            for tx in b.transactions:
                # print(str(tx.tx_id))
                # print(transaction)
                # print(str(tx.tx_id)[1:])
                # print(transaction[2:-2])
                if str(tx.tx_id) == transaction:
                    return tx
            # if len(b.prev_block_hash) == 0:
            #     break

    def sing_transaction(self, tx, privkey):
        prev_txs = {}
        for i in tx.inputs:
            prev_tx = self.find_transaction(i.tx_id)
            prev_txs[prev_tx.tx_id] = prev_tx
        tx.sign(privkey, prev_txs)

    def verify_transaction(self, tx):
        prev_txs = {}
        for i in tx.inputs:
            prev_tx = self.find_transaction(i.tx_id)
            prev_txs[prev_tx.tx_id] = prev_tx
        return tx.verify(prev_txs)

    def serialize(self):
        with open("blockchain.txt", mode="wb") as f:
            pickle.dump(self, f)

    def deserialize(self):
        with open("blockchain.txt", mode="rb") as f:
            obj_data = pickle.load(f)
        self.blocks = obj_data.blocks
        pass


if __name__ == "__main__":

    # w1 = Wallet()
    # address_1 = w1.generate_address()
    # print("Address_1 = " + str(address_1) + "\n")
    #
    # w2 = Wallet()
    # address_2 = w2.generate_address()
    # print("Address_2 = " + str(address_2) + "\n")
    ws = Ws.Wallets()
    address_1 = ws.create_wallet()
    # ws.wallets[0].generate_address()
    ws.serialize()
    bc = Blockchain(address_1)

    address_2 = ws.create_wallet()
    print("Address_1 = " + str(address_1) + "\n")
    print("Address_2 = " + str(address_2) + "\n")
    print("Balance 1: " + str(bc.get_balance(address_1)))
    print("Balance 2: " + str(bc.get_balance(address_2)))
    bc.add_block(address_2)

    bc.send(address_1, address_2, 1)

    print("A1 balance: " + str(bc.get_balance(address_1)))

    print("A2 balance: " + str(bc.get_balance(address_2)))

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
