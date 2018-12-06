import hashlib

# Hash pairs of items recursively until a single value is obtained
def merkle(hashList):
    if len(hashList) == 1:
        return hashList[0]
    newHashList = []
    # Process pairs. For odd length, the last is skipped
    for i in range(0, len(hashList)-1, 2):
        newHashList.append(hash2(hashList[i], hashList[i+1]))
    if len(hashList) % 2 == 1: # odd, hash last item twice
        newHashList.append(hash2(hashList[-1], hashList[-1]))
    return merkle(newHashList)

def hash2(a, b):
    # Reverse inputs before and after hashing
    # due to big-endian / little-endian nonsense
    a1 = a.encode()
    b1 = b.encode()
    h = hashlib.sha256(hashlib.sha256(a1 + b1).digest()).hexdigest()
    return h


hl = []
hl.append("a29e4e707185019f88932d")
hl.append("382c44e4581179ae33ea")
print(merkle(hl))