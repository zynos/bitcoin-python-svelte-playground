import uvicorn
from base64 import decode
from cgi import print_form
from sys import path_importer_cache
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from create_invoice import create_invoice, get_invoice
import qrcode
import json
import base64
from io import BytesIO
import time

path_to_btc_cookie = "/home/admin/.bitcoin/.cookie"
use_electrum = False
if use_electrum:
    # electrum server port
    PORT = 50001
else:
    # bitcoin cli port
    PORT = 8332


def read_auth_cookie() -> str:
    with open(path_to_btc_cookie, "r") as f:
        cookie = f.read()
    return cookie


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
    start = time.time()
    verbose = True
    mem_transactions = rpc_connection.getrawmempool(verbose)
    print("mempool fetch took", time.time()-start)
    detail_transactions = []
    print("current transactions", len(mem_transactions))
    if verbose:
        tx_ids = [id for id in mem_transactions.keys()]
    else:
        tx_ids = mem_transactions

    invalid_trxs = []
    for id in tx_ids[:100]:
        try:
            transaction = rpc_connection.getrawtransaction(id, True)
            detail_transactions.append(transaction)

        except:
            invalid_id = id
            invalid_trx = mem_transactions[invalid_id]
            invalid_trxs.append(invalid_trx)

    # commands = [["getrawtransaction", id, True]
    #             for id in mem_transactions.keys()]

    # start = time.time()
    # detail_transactions = rpc_connection.batch_(commands)
    # print("mempool detail fetch took",time.time()-start)
    detail_transactions_dict = {el["txid"]: el for el in detail_transactions}

    compress_trx = []
    for key, value in detail_transactions_dict.items():
        # might encounter bitcoinrpc.authproxy.JSONRPCException: -5: No such mempool or blockchain transaction.
        try:
            if verbose:
                fee_in_sats = float(mem_transactions[key]["fee"]) * 100000000
                vsize = value["vsize"]
                sat_per_vbyte = round(fee_in_sats / vsize, 1)
                btc_moved = sum([el["value"]
                                for el in detail_transactions_dict[key]["vout"]])
                compressed = {key: {"fee": fee_in_sats, "sat_per_vbyte": sat_per_vbyte,
                                    "vsize": vsize, "btc_moved": btc_moved}}
                compress_trx.append(compressed)
        except:
            pass

    print("returning", len(detail_transactions), "transactions")

    return {"mempool_trxs": detail_transactions, "compressed": compress_trx}


@app.get("/invoice/{sat_amount}")
def get_invoice_qr_code(sat_amount: int):
    buffered = BytesIO()
    invoice_dict = create_invoice(sat_amount)
    print(invoice_dict)
    qr_image = qrcode.make(invoice_dict["paymentRequest"])
    qr_image.save(buffered, format="png")
    img_str = base64.b64encode(buffered.getvalue())
    decoded = img_str.decode("ascii")
    decoded = "data:image/png;base64,"+decoded
    invoice_dict["payment_request_qr"] = decoded
    return invoice_dict


@app.get("/invoice_paid/{add_index}")
def check_for_payment(add_index: int):
    invoice_dict = get_invoice(add_index)
    print(invoice_dict)
    if "settled" in invoice_dict.keys() and invoice_dict["settled"]:
        return {"settled": True, "quoute": "An apple a day keeps the doctor away"}
    else:
        return {"settled": False}


@app.get("/get_dummy_invoice")
def get_invoice_qr_code():

    buffered = BytesIO()

    pay_req = "lnbc100u1p383wdppp52d9rgd2vkmv355jw35vd5q0k3cc80v9yvxvgkt9cf50ez7tyxqxsdp2f3hkxctv94fx2cnpd3skucm995cnqvpsxqk4xct5wvcqzpgxqrrsssp5ql0de9uzejf2dj0kcknc5thtp7hdr4ekeyc6l6u36ctz3squ0sjs9qyyssq26vjm03jtzh28teh7pkvth2x3pwdp96zejdwwyuwkpr5vljw3c8rhy9t205f84pydpwe5dajd9898fvlu4cpuxf0gmjd7lyg50f3gcqqn89xd9"
    invoice_dict = {"payment_request": pay_req}
    qr_image = qrcode.make(invoice_dict["payment_request"])
    qr_image.save(buffered, format="png")
    img_str = base64.b64encode(buffered.getvalue())
    decoded = img_str.decode("ascii")
    print(img_str)
    print(decoded)
    invoice_dict["payment_request_qr"] = "data:image/png;base64,"+decoded
    return invoice_dict


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
