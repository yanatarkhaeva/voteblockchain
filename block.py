import time
from voteblockchain.pow import ProofOfWork


class Block:
    def __init__(self, prev_block_hash, transactions, nonce=0):
        self.timestamp = time.time()
        self.prev_block_hash = prev_block_hash
        self.transactions = transactions
        self.hash = ""
        self.nonce = nonce

    def set_hash(self):
        pow = ProofOfWork(self)
        self.nonce, self.hash = pow.run()
        # print(self.timestamp)
        # print(self.data)
        # print(self.prev_block_hash)
        # headers = str(self.timestamp) + str(self.data) + str(self.prev_block_hash)
        # print(headers)
        # new_hash = hashlib.md5(headers.encode("utf-8")).hexdigest()
        # print(new_hash)
        # return new_hash


if __name__ == "__main__":
    block = Block("datat", "5f4dcc3b5aa765d61d8327deb882cf99")
