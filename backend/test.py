from cgi import print_form
from sys import path_importer_cache
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from create_invoice import create_invoice, get_invoice
import qrcode
import json

path_to_btc_cookie = "/home/admin/.bitcoin/.cookie"


def read_auth_cookie() -> str:
    with open(path_to_btc_cookie, "r") as f:
        cookie = f.read()
    return cookie

use_electrum = False
if use_electrum:
    # electrum server port
    PORT = 50001
else:
    # bitcoin cli port
    PORT = 8332
combined_auth = read_auth_cookie()
# rpc_user and rpc_password are set in the bitcoin.conf file
connect_string = f"http://{combined_auth}@127.0.0.1:{PORT}"

onnect_string = f"http://{combined_auth}@127.0.0.1:{PORT}"
rpc_connection = AuthServiceProxy(connect_string)
mem_transactions = rpc_connection.getrawmempool(True)
keys = list(mem_transactions.keys())
detail_transactions = []
print("current transactions", len(mem_transactions))
commands = [["getrawtransaction", id, True] for id in mem_transactions]
try:
    detail_transactions = rpc_connection.batch_(commands)
except:
    print("fetching mempool failed")
    pass

origins = [
    "*"
]
app = FastAPI()
print("created app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/dict")
async def get_dict():
    combined_auth = read_auth_cookie()
    connect_string = f"http://{combined_auth}@127.0.0.1:{PORT}"
    # rpc_user and rpc_password are set in the bitcoin.conf file
    rpc_connection = AuthServiceProxy(connect_string)
    mem_transactions = rpc_connection.getrawmempool(True)
    return {"mempool_trxs": mem_transactions}


@app.get("/")
async def root():
    combined_auth = read_auth_cookie()
    # rpc_user and rpc_password are set in the bitcoin.conf file
    connect_string = f"http://{combined_auth}@127.0.0.1:{PORT}"
    rpc_connection = AuthServiceProxy(connect_string)
    mem_transactions = rpc_connection.getrawmempool(True)
    detail_transactions = []
    print("current transactions", len(mem_transactions))
    commands = [["getrawtransaction", id, True]
                for id in mem_transactions.keys()]
    detail_transactions = rpc_connection.batch_(commands)
    detail_transactions_dict = {el["txid"]: el for el in detail_transactions}

    compress_trx = []
    for key, value in mem_transactions.items():
        # might encounter bitcoinrpc.authproxy.JSONRPCException: -5: No such mempool or blockchain transaction.
        try:
            fee_in_sats = float(value["fee"]) * 100000000
            btc_moved = sum([el["value"]
                            for el in detail_transactions_dict[key]["vout"]])
            compressed = {key: {"fee": fee_in_sats,
                                "vsize": value["vsize"], "btc_moved": btc_moved}}
            compress_trx.append(compressed)
        except:
            pass

    print("returning", len(detail_transactions), "transactions")

    return {"mempool_trxs": detail_transactions, "compressed": compress_trx}


@app.get("/invoice/{sat_amount}")
def get_invoice_qr_code(sat_amount: int):
    invoice_dict = create_invoice(sat_amount)
    print(invoice_dict)
    qr_image = qrcode.make(invoice_dict["paymentRequest"])
    image_str = json.dumps(qr_image.tobytes().decode("latin1"))
    invoice_dict["payment_request_qr"] = image_str
    return invoice_dict

@app.get("/invoice_paid/{add_index}")
def check_for_payment(add_index: int):
    invoice_dict = get_invoice(add_index)
    print(invoice_dict)
    if "settled" in invoice_dict.keys() and invoice_dict["settled"]:
        return {"settled":True,"quoute":"An apple a day keeps the doctor away"}
    else:
        return {"settled":False}
