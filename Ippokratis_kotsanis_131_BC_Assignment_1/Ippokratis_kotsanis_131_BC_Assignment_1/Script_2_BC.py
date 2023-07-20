from bitcoinutils.setup import setup
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence
from bitcoinutils.keys import P2pkhAddress, P2shAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_ABSOLUTE_TIMELOCK
from bitcoinutils.utils import to_satoshis
import time
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from bitcoinutils.proxy import NodeProxy


def create_p2pkh_adress_to_send_funds():
    # create a private key (deterministically)
    priv2_key = PrivateKey(secret_exponent = 2)

    # get the corresponding public key
    pub = priv2_key.get_public_key()

    # create a P2PKH address from the public key
    p2pkh_addr = pub.get_address()

    p2pkh_addr_send_string = p2pkh_addr.to_string()
    
    p2pkh_addr_send = P2pkhAddress(p2pkh_addr_send_string)

    return p2pkh_addr_send


def create_p2sh_address_timelock_abs(p2pkh_pubkey, epoch_time):
    # set values
    locktime = int(epoch_time)
    seq = Sequence(TYPE_ABSOLUTE_TIMELOCK, locktime)

    # get the address (from the public key)
    p2pkh_addr = p2pkh_pubkey.get_address()

    # create the redeem script
    redeem_script = Script([seq.for_script(), 'OP_CHECKLOCKTIMEVERIFY', 'OP_DROP', 'OP_DUP', 'OP_HASH160', p2pkh_addr.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])

    # create a P2SH address from a redeem script
    addr = P2shAddress.from_script(redeem_script)
	
    #return list of def
    returnList = [addr, seq, redeem_script]

    return returnList
    

def get_inputs_Of_Address(rpc_connection, addrs):
    # Get unspent outputs for the P2SH address
    unspent_outputs = rpc_connection.scantxoutset("start", ["addr({})".format(addrs)])
    
    sum = 0
    txids_list = unspent_outputs["unspents"]
    utxos = unspent_outputs
   
    for utxo in txids_list:
        sum += utxo['amount']
        txid = utxo["txid"]
        vout = utxo["vout"]
        amount = utxo["amount"]
        height = utxo["height"]
            
    return txids_list, sum
    
    
def add_txins(txids_list, seq):
    # List of inputs
    txins_list = []

    for txid in txids_list:
        txin = TxInput(txid["txid"], txid["vout"], sequence=seq.for_input_sequence())
        txins_list.append(txin)

    return txins_list


def main():
    # always remember to set up the network
    setup('regtest')

    # set values
    fee_rate = 0.0001  # BTC per byte  

    # get private key from user input - # private key to sign the spending transaction
    priv_key_wif = input("Enter private key WIF: ")
    
    # validation check 1
    if not priv_key_wif or len(priv_key_wif) != 51:
        print("Invalid private key")
        exit()

    # validation check 2 - (Check if private key is valid)
    try:
        priv_key_sk = PrivateKey.from_wif(priv_key_wif)
    except ValueError:
        print("Invalid private key.")
        exit() 
    
    # set values
    p2pkh_wif = priv_key_sk.to_wif(compressed=False)

    # get private key and public key from WIF
    p2pkh_sk = PrivateKey.from_wif(p2pkh_wif)
    p2pkh_pubkey = p2pkh_sk.get_public_key()   

    #epoch_time = 1697958400  # July 20th, 2023 at 12:00:00 AM UTC
    epoch_time  = input("Enter epoch time ( e.g. 1697958400) : ")
     
    # create a P2SH address with absolute timelock - same with output from script 1
    p2sh_addr, seq, redeemScript = create_p2sh_address_timelock_abs(p2pkh_pubkey, epoch_time)
    
    # use a library - bitcoinrpc to interact with a local Bitcoin Core node, which allows you to query the blockchain directly
    # Connect to the local Bitcoin Core node - credentials are in bitcoin.config file
    rpc_user = 'rpcuser'
    rpc_password = 'ippo1998'
    rpc_connection = AuthServiceProxy(f'http://{rpc_user}:{rpc_password}@127.0.0.1:18443')
    
    #load the wallet that was created
    #rpc_connection.loadwallet('mynewwallet_BC')
    
    #loadWallet - add inputs to the transaction
    txids_list, sum = get_inputs_Of_Address(rpc_connection, p2sh_addr.to_string()) 

    # P2PKH address to send the funds to
    p2pkh_addr_send = create_p2pkh_adress_to_send_funds()
    
    # Estimated funds you have
    print('Estimated funds you have: '+str(sum)+' BTCs\n')

    # Send BTCs
    BTCsToSend = float(input('Enter BTCs to send to given P2KH address: '))
    
    # Add inputs to the transaction   
    txins_list = add_txins(txids_list, seq)
    
    # Add output to the transaction
    txout = TxOutput(to_satoshis(BTCsToSend), p2pkh_addr_send.to_script_pub_key())
    
    # Create transaction object
    tx = Transaction(txins_list, [txout])

    # calculate fee and update output value
    tx_size = tx.get_size()
    fee = float(fee_rate * tx_size)
    amount = to_satoshis(BTCsToSend) - to_satoshis(fee)
    txout = TxOutput(amount, p2pkh_addr_send.to_script_pub_key())
    # Update output value with fee
    tx = Transaction(txins_list, [txout])
    
    # print transaction details - Raw unsigned transaction
    print("Raw unsigned transaction:\n" + tx.serialize())
    
    # Sign transaction inputs
    for i in range(len(txins_list)):
        sig = p2pkh_sk.sign_input(tx, i, redeemScript)
        txins_list[i].script_sig = Script([sig, p2pkh_sk.get_public_key().to_hex(), redeemScript.to_hex()])
    
    # Print raw signed transaction
    print("\nRaw signed transaction:\n" + tx.serialize())
    
    # Get the transaction id
    txid = tx.get_txid()
    print("\nTransaction id:\n" + txid)
        
    # Validate transaction - Submit the transaction to the mempool
    result = rpc_connection.testmempoolaccept([tx.serialize()])

    # Check if the transaction is valid
    if result[0].get("allowed", False):
        print("\nTransaction is valid and was added to the mempool.\n")
        # Broadcast transaction to the Bitcoin network
        TXID = rpc_connection.sendrawtransaction(tx.serialize())
        print("\nBroadcasting was successfuly done!\n")
    else:
        print("\nTransaction is invalid and was not added to the mempool.\n")
    
    
    
if __name__ == "__main__":
    main()
    
    
    
    
