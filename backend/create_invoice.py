import codecs
import json
import grpc
import os
from google.protobuf.json_format import MessageToDict
from pkg_resources import safe_extra
# to generate the 2 following files see --> https://api.lightning.community/#addinvoice
import lightning_pb2 as lnrpc
import lightning_pb2_grpc as lightningstub

LNDIR = "/data/lnd/"

macaroon = codecs.encode(
    open(LNDIR+'data/chain/bitcoin/mainnet/admin.macaroon', 'rb').read(), 'hex')
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
cert = open(LNDIR+'tls.cert', 'rb').read()

ssl_creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('localhost:10009', ssl_creds)
stub = lightningstub.LightningStub(channel)


def create_invoice(sat_amount=2) -> dict:
    request = lnrpc.Invoice(value=sat_amount)
    response = stub.AddInvoice(request, metadata=[('macaroon', macaroon)])
    response = MessageToDict(response)
    print(response)
    return response

def subscribe_to_invoice():
    r_hash = "84b49832b3429bd1963af989b2f11c6cc34ec4f3d4af585166af438bd3214044".encode("utf-8")
    request = lnrpc.InvoiceSubscription(add_index=41)
    for response in stub.SubscribeInvoices(request, metadata=[('macaroon', macaroon)]):
        dict_obj = MessageToDict(response)
        print(dict_obj)

def get_invoice(index_offset: int):
    request = lnrpc.ListInvoiceRequest(index_offset=index_offset-1)
    response = stub.ListInvoices(request, metadata=[('macaroon', macaroon)])
    invoice = response.invoices[0]
    print(invoice)
    print(invoice.settled)
    print(type(invoice))
    invoice = MessageToDict(invoice)
    print(invoice)
    return invoice
