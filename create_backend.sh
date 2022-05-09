cd backend
echo "create virtual py environment and install dependencies ..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
git clone https://github.com/googleapis/googleapis.git
curl -o lightning.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/lightning.proto
python -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. lightning.proto
