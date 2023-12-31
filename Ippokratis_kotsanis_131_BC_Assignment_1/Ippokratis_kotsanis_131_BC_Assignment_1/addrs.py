from bitcoinutils.setup import setup
from bitcoinutils.keys import P2pkhAddress, PrivateKey, PublicKey

setup('regtest')
# create a private key (deterministically)
priv = PrivateKey(secret_exponent = 1)
# compressed is the default
print("\nPrivate key WIF:", priv.to_wif(compressed=False))

# create a private key (deterministically)
#priv2 = PrivateKey(secret_exponent = 2)
# compressed is the default
#print("\nPrivate key WIF 2:", priv2.to_wif(compressed=False))

# get the public key
pub = priv.get_public_key()
# compressed is the default
print("Public key:", pub.to_hex(compressed=True))
# get address from public key
address = pub.get_address()
# print the address and hash160 - default is compressed address
print("Address:", address.to_string())
print("Hash160:", address.to_hash160())
