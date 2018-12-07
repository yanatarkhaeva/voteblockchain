import hashlib
import pickle

import base58
import ecdsa


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


class Coinbase:
    subsidy = 1

    def __init__(self, to, data=""):
        self.tx_id = None
        if data == "":
            data = "Reward to " + str(to)
        # self.tx_id = id
        self.inputs = []
        self.outputs = []
        self.inputs.append(TXInput(1, 0, data, data))
        self.outputs.append(TXOutput(Coinbase.subsidy, to))

    def set_id(self):
        self.tx_id = self.hashhash()

    def hashhash(self):
        #  сериализует транзакцию и хеширует ее с помощью алгоритма SHA-256.
        #  Результатом являются данные готовые для подписи.
        serialized = pickle.dumps(self)
        hashed = hashlib.sha256(serialized).hexdigest().encode()
        return hashed

    def can_unlock_output_with(self, i, unlocking_data):
        return self.inputs[i].signature == unlocking_data

    def can_be_unlocked_with(self, i, unlocking_data):
        return self.outputs[i].pub_key_hash == unlocking_data

    def sign(self, priv_key, prev_txs):
        tx_copy = self.trimmed_copy()
        for i in self.inputs:
            for k in prev_txs.keys():
                if str(k) == i.tx_id:
                    prev_tx = prev_txs[k]
            tx_copy.inputs[self.inputs.index(i)].signature = None
            tx_copy.inputs[self.inputs.index(i)].pub_key = prev_tx.outputs[int(i.vout)].pub_key_hash
            print("To sign raw: ")
            print("----" + str(tx_copy.tx_id))
            for ii in tx_copy.inputs:
                print("----" + str(ii.pub_key))
                print("----" + str(ii.tx_id))
                print("----" + str(ii.vout))
            for out in tx_copy.outputs:
                print("====" + str(out.value))
                print("====" + str(out.pub_key_hash))
            tx_copy.tx_id = tx_copy.hashhash()
            tx_copy.inputs[self.inputs.index(i)].pub_key = None
            print("To sign: ", str(tx_copy.tx_id))
            # TODO: r, s, err := ecdsa.Sign(rand.Reader, &privKey, txCopy.ID)
            # sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
            # vk = sk.get_verifying_key()
            sk = ecdsa.SigningKey.from_string(priv_key, curve=ecdsa.SECP256k1)
            sig = sk.sign(tx_copy.tx_id)
            print("Signature:  " + str(sig.hex()))
            # pk = coincurve.PrivateKey.from_hex(priv_key)
            # signature = pk.sign(tx_copy.tx_id)
            i.signature = sig.hex()

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
            for k in prev_txs.keys():
                if str(k) == i.tx_id:
                    prev_tx = prev_txs[k]
            # prev_tx = prev_txs[i.tx_id]  # возможно, тут нужно что-нить hex() или encode()/decode()
            tx_copy.inputs[self.inputs.index(i)].signature = None
            tx_copy.inputs[self.inputs.index(i)].pub_key = prev_tx.outputs[int(i.vout)].pub_key_hash
            print("To verify raw: ")
            print("----" + str(tx_copy.tx_id))
            for ii in tx_copy.inputs:
                print("----" + str(ii.pub_key))
                print("----" + str(ii.tx_id))
                print("----" + str(ii.vout))
            for out in tx_copy.outputs:
                print("====" + str(out.value))
                print("====" + str(out.pub_key_hash))
            tx_copy.tx_id = tx_copy.hashhash()
            tx_copy.inputs[self.inputs.index(i)].pub_key = None
            print("To verify: " + str(tx_copy.tx_id))
            print("Signature: " + str(i.signature))
            vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(i.pub_key), curve=ecdsa.SECP256k1)
            try:
                vk.verify(bytes.fromhex(i.signature), tx_copy.tx_id)
            except ecdsa.keys.BadSignatureError:
                return False
        return True


class Transaction:
    def __init__(self, inputs, outputs):
        self.tx_id = None
        self.inputs = inputs
        self.outputs = outputs

    def set_id(self):
        self.tx_id = self.hashhash()

    def can_unlock_output_with(self, i, unlocking_data):
        return self.inputs[i].signature == unlocking_data

    def can_be_unlocked_with(self, i, unlocking_data):
        return self.outputs[i].script_pub_key == unlocking_data

    def sign(self, priv_key, prev_txs):
        tx_copy = self.trimmed_copy()
        for i in self.inputs:
            for k in prev_txs.keys():
                if str(k) == i.tx_id:
                    prev_tx = prev_txs[k]
            tx_copy.inputs[self.inputs.index(i)].signature = None
            tx_copy.inputs[self.inputs.index(i)].pub_key = prev_tx.outputs[int(i.vout)].pub_key_hash
            print("To sign raw: ")
            print("----" + str(tx_copy.tx_id))
            for ii in tx_copy.inputs:
                print("----" + str(ii.pub_key))
                print("----" + str(ii.tx_id))
                print("----" + str(ii.vout))
            for out in tx_copy.outputs:
                print("====" + str(out.value))
                print("====" + str(out.pub_key_hash))
            tx_copy.tx_id = tx_copy.hashhash()
            tx_copy.inputs[self.inputs.index(i)].pub_key = None
            print("To sign: ", str(tx_copy.tx_id))
            # TODO: r, s, err := ecdsa.Sign(rand.Reader, &privKey, txCopy.ID)
            # sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
            # vk = sk.get_verifying_key()
            sk = ecdsa.SigningKey.from_string(priv_key, curve=ecdsa.SECP256k1)
            sig = sk.sign(tx_copy.tx_id)
            print("Signature:  " + str(sig.hex()))
            # pk = coincurve.PrivateKey.from_hex(priv_key)
            # signature = pk.sign(tx_copy.tx_id)
            i.signature = sig.hex()

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
            for k in prev_txs.keys():
                if str(k) == i.tx_id:
                    prev_tx = prev_txs[k]
            # prev_tx = prev_txs[i.tx_id]  # возможно, тут нужно что-нить hex() или encode()/decode()
            tx_copy.inputs[self.inputs.index(i)].signature = None
            tx_copy.inputs[self.inputs.index(i)].pub_key = prev_tx.outputs[int(i.vout)].pub_key_hash
            print("To verify raw: ")
            print("----" + str(tx_copy.tx_id))
            for ii in tx_copy.inputs:
                print("----" + str(ii.pub_key))
                print("----" + str(ii.tx_id))
                print("----" + str(ii.vout))
            for out in tx_copy.outputs:
                print("====" + str(out.value))
                print("====" + str(out.pub_key_hash))
            tx_copy.tx_id = tx_copy.hashhash()
            tx_copy.inputs[self.inputs.index(i)].pub_key = None
            print("To verify: " + str(tx_copy.tx_id))
            print("Signature: " + str(i.signature))
            vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(i.pub_key), curve=ecdsa.SECP256k1)
            try:
                vk.verify(bytes.fromhex(i.signature), tx_copy.tx_id)
            except ecdsa.keys.BadSignatureError:
                return False
        return True

        #     pub = coincurve.PublicKey(i.pub_key)
        #     if not coincurve.verify_signature(i.signature, tx_copy.tx_id, pub.format()):
        #         # if not pub.verify(i.signature, tx_copy.tx_id):
        #         return False
        # return True
    pass
