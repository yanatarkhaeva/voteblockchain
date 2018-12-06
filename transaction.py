import hashlib
import pickle
import secrets

import base58
import coincurve


# TXOutput = namedtuple("TXOutput", ["value", "pub_key_hash"])
# TXInput = namedtuple("TXInput", ["tx_id", "out_to", "script_sig", "pub_key"])


class TXOutput:
    def __init__(self, value, pub_key_hash):
        self.value = value
        self.pub_key_hash = pub_key_hash

    def lock(self, address):
        self.pub_key_hash = base58.b58decode(address)
        print(self.pub_key_hash)
        self.pub_key_hash = self.pub_key_hash[1:-4]
        print(self.pub_key_hash)

    def is_locked_with_key(self, pubkeyhash):
        return self.pub_key_hash == pubkeyhash


class TXInput:
    def __init__(self, tx_id, vout, signature, pub_key):
        self.tx_id = tx_id
        self.vout = vout
        self.signature = signature
        self.pub_key = pub_key

    def uses_key(self, pub_key_hash):
        pass


# class TrasactionBase:
#     id_iterator = 0
#
#     def __init__(self):
#         self.tx_id = TrasactionBase.id_iterator
#         TrasactionBase.id_iterator += 1
#         pass


class Coinbase:
    subsidy = 1

    def __init__(self, to, data=""):
        self.tx_id = secrets.token_bytes(64)
        if data == "":
            data = "Reward to " + str(to)
        # self.tx_id = id
        self.inputs = []
        self.outputs = []
        self.inputs.append(TXInput(1, 0, data, data))
        self.outputs.append(TXOutput(Coinbase.subsidy, to))

    def can_unlock_output_with(self, i, unlocking_data):
        return self.inputs[i].signature == unlocking_data

    def can_be_unlocked_with(self, i, unlocking_data):
        return self.outputs[i].pub_key_hash == unlocking_data


class Transaction:
    def __init__(self, inputs, outputs):
        self.tx_id = secrets.token_bytes(64)
        self.inputs = inputs
        self.outputs = outputs

    def can_unlock_output_with(self, i, unlocking_data):
        return self.inputs[i].signature == unlocking_data

    def can_be_unlocked_with(self, i, unlocking_data):
        return self.outputs[i].script_pub_key == unlocking_data

    def sign(self, priv_key, prev_txs):
        tx_copy = self.trimmed_copy()
        for i in self.inputs:
            prev_tx = prev_txs[i.tx_id]
            tx_copy.inputs[self.inputs.index(i)].signature = None
            tx_copy.inputs[self.inputs.index(i)].pub_key = prev_tx.outputs[i.vout].pub_key_hash
            tx_copy.tx_id = tx_copy.hashhash()
            tx_copy.inputs[self.inputs.index(i)].pub_key = None

            # TODO: r, s, err := ecdsa.Sign(rand.Reader, &privKey, txCopy.ID)
            pk = coincurve.PrivateKey.from_hex(priv_key)
            signature = pk.sign(tx_copy.tx_id)
            i.signature = signature

    def hashhash(self):
        #  сериализует транзакцию и хеширует ее с помощью алгоритма SHA-256.
        #  Результатом являются данные готовые для подписи.
        serialized = pickle.dumps(self)
        hashed = hashlib.sha256(serialized).hexdigest().encode()
        return hashed

    def trimmed_copy(self):
        ins = []
        outs = []
        for inn in self.inputs:
            ins.append(TXInput(inn.tx_id, inn.vout, None, None))
        for out in self.outputs:
            outs.append(TXOutput(out.value, out.pub_key_hash))
        tx_copy = Transaction(ins, outs)
        return tx_copy

    def verify(self, prev_txs):
        tx_copy = self.trimmed_copy()

        for i in self.inputs:
            prev_tx = prev_txs[i.tx_id]  # возможно, тут нужно что-нить hex() или encode()/decode()
            tx_copy.inputs[self.inputs.index(i)].signature = None
            tx_copy.inputs[self.inputs.index(i)].pub_key = prev_tx.outputs[i.vout].pub_key_hash
            tx_copy.tx_id = tx_copy.hashhash()
            tx_copy.inputs[self.inputs.index(i)] = None

            #  verify


    pass