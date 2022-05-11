# How to generate a lightning invoice with python
## 1 - Connect to LND via gRPC
```
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
```
## 2 - send a gRPC command to create an invoice
```
def create_invoice(sat_amount=2) -> dict:
    request = lnrpc.Invoice(value=sat_amount)
    response = stub.AddInvoice(request, metadata=[('macaroon', macaroon)])
    response = MessageToDict(response)
    print(response)
    return response
```
With the `create_invoice()` you can generate a new invoice for N satoshis. The result you get looks similar to this:
```
>>> create_invoice(sat_amount=2)
{ 
    "r_hash": <bytes>,
    "payment_request": <string>,
    "add_index": <uint64>,
    "payment_addr": <bytes>,
}
```
Here, the field `payment_request` contains a string which could look like this:
```
payment_request = "lnbc100u1p383wdppp52d9rgd2vkmv355jw35vd5q0k3cc80v9yvxvgkt9cf50ez7tyxqxsdp2f3hkxctv94fx2cnpd3skucm995cnqvpsxqk4xct5wvcqzpgxqrrsssp5ql0de9uzejf2dj0kcknc5thtp7hdr4ekeyc6l6u36ctz3squ0sjs9qyyssq26vjm03jtzh28teh7pkvth2x3pwdp96zejdwwyuwkpr5vljw3c8rhy9t205f84pydpwe5dajd9898fvlu4cpuxf0gmjd7lyg50f3gcqqn89xd9"
```
This string can be read by every lightning wallet and can be easily transformed into a QR code by every string to QR code converter.
## 3 Create QR code
In python this could be done with the 
[qrcode](hhttps://pypi.org/project/qrcode/) package.

```
import qrcode

qr_image = qrcode.make(payment_request)
```
save image to a file 
```
qr_image.save("some_file.png")
```

or encode it and send it to an HTML frontend
```
image_str = json.dumps(qr_image.tobytes().decode("latin1"))
invoice_dict["payment_request_qr"] = image_str
```