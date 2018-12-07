import hashlib

import base58
import ecdsa


class Wallet:
    def __init__(self):
        self.private, self.public = self.new_key_pair()

    def new_key_pair(self):
        sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)  # private ключ
        private_key = sk.to_string()  # конвертим private ключ в hex
        vk = sk.get_verifying_key()  # public ключ
        public_key = vk.to_string().hex()
        return private_key, public_key

    def generate_address(self):
        # pubkey = self.hash_pub_key(self.public)
        khash = self.hash_pub_key(self.public)
        checksum = self.hash_pub_key(khash.hexdigest())
        preaddress = "00" + khash.hexdigest() + checksum.hexdigest()
        public_key = base58.b58encode(preaddress.encode())
        return public_key

    def hash_pub_key(self, key):
        pubkey = key.encode()
        pub = hashlib.sha256(pubkey)
        p = hashlib.new("ripemd160")
        p.update(pub.hexdigest().encode())
        p.hexdigest()
        return p
        # print("Wallet address / Public key: {0}".format(public_key))



if __name__ == "__main__":
    w = Wallet()
    print(w.generate_address())