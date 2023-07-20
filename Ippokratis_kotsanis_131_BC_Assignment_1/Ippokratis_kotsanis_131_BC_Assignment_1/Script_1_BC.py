from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey, PublicKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK, SIGHASH_ALL


def create_p2sh_address_timelock_abs(p2pkh_pubkey, epoch_time):
    # set values
    locktime = int(epoch_time)
    
    seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, locktime)

    # get the address (from the public key)
    p2pkh_addr = p2pkh_pubkey.get_address()

    # create the redeem script
    redeem_script = Script([seq.for_script(),'OP_CHECKLOCKTIMEVERIFY','OP_DROP','OP_DUP','OP_HASH160',p2pkh_addr.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])

    # create a P2SH address from a redeem script
    addr = P2shAddress.from_script(redeem_script)

    return addr.to_string()


def main():
    # always remember to setup the network
    setup('regtest')
    
    # get private key from user input
    priv_key_wif = input("Enter private key WIF: ")
    priv_key = PrivateKey.from_wif(priv_key_wif)
    
    # set values
    p2pkh_wif = priv_key.to_wif(compressed=False)
    
    #epoch_time = 1697958400  # July 20th, 2023 at 12:00:00 AM UTC
    epoch_time  = input("Enter epoch time (e.g. 1697958400) : ")

    # get private key and public key from WIF
    p2pkh_sk = PrivateKey.from_wif(p2pkh_wif)
    p2pkh_pubkey = p2pkh_sk.get_public_key()

    # create the P2SH address
    addr = create_p2sh_address_timelock_abs(p2pkh_pubkey, epoch_time)

    print("P2SH address:", addr)


if __name__ == "__main__":
    main()
