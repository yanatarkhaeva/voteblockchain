import sys
import hashlib
import struct


class ProofOfWork:
    target_bits = 69

    def __init__(self, block):
        self.block = block
        self.target = 1 << 256 - ProofOfWork.target_bits
        pass
    #
    # def prepare_data(self):
    #     hexed_prev_hash = str(self.block.prev_block_hash)
    #     hexed_transaction = self.transactions_to_hex()
    #     hexed_timestamp = hex(int(self.block.timestamp))[2:]
    #     hexed_target_bits = hex(ProofOfWork.target_bits)[2:]
    #     hexed_nonce = hex(self.block.nonce)[2:]
    #     # print(hexed_prev_hash)
    #     # print(hexed_data)
    #     # print(hexed_timestamp)
    #     # print(hexed_target_bits)
    #     # print(hexed_nonce)
    #     hexx = str(hexed_prev_hash + hexed_transaction + hexed_timestamp + hexed_target_bits + hexed_nonce)
    #     # print(hexx)
    #     # hexx =  hashlib.sha256(hexx.encode()).hexdigest()
    #     return hexx

    def transactions_to_hex(self):
        thashed = ""
        for i in self.block.transactions:
            thashed += str(i.tx_id)
        return thashed


    def run(self):
        nonce = 0

        while nonce < 0x100000000:  # 2**32
            header = (self.block.prev_block_hash[::-1] + self.transactions_to_hex()
                      + struct.pack("<LL", int(self.block.timestamp), nonce).hex())
            hash = hashlib.sha256(hashlib.sha256(header.encode()).digest()).hexdigest()

            # sys.stdout.write("\rNonce: {}, hash: {}".format(nonce, hash[::-1]))
            # sys.stdout.flush()

            target_hexstr = 1 << (256 - ProofOfWork.target_bits)
            target_str = hex(target_hexstr)

            if hash[::-1] < target_str:
                # print('\nSuccess!')
                break
            nonce += 1

        return nonce, hash[::-1]