from flask import Flask, jsonify, request
import os
import binascii
import ecdsa
import hashlib
from ecdsa.util import sigencode_der_canonize, sigdecode_string

app = Flask(__name__)

with open("device_public_key.pem", "rb") as f:
    public_key = ecdsa.VerifyingKey.from_pem(f.read())

 
challenges = {}

@app.route('/authenticate', methods=['GET'])
def authenticate():
    client_ip = request.remote_addr   
    challenge = os.urandom(16)   
    challenges[client_ip] = challenge   
    challenge_hex = binascii.hexlify(challenge).decode()

    print(f"✅ Sent Challenge to {client_ip}: {challenge_hex}")   
    return jsonify({"challenge": challenge_hex})

@app.route('/verify', methods=['POST'])
def verify():
    client_ip = request.remote_addr
    data = request.json
    if "signature" not in data:
        return jsonify({"status": "error", "message": "Missing signature"}), 400

     
    if client_ip not in challenges:
        return jsonify({"status": "error", "message": "No challenge found"}), 400
    challenge = challenges.pop(client_ip)   

     
    hash_obj = hashlib.sha3_256(challenge)
    hash_digest = hash_obj.digest()

    
    try:
        raw_signature = binascii.unhexlify(data["signature"])
        if len(raw_signature) != 64:
            return jsonify({"status": "error", "message": "Invalid signature length"}), 400
    except binascii.Error:
        return jsonify({"status": "error", "message": "Invalid signature format"}), 400

     
    r = int.from_bytes(raw_signature[:32], byteorder="big")
    s = int.from_bytes(raw_signature[32:], byteorder="big")
    der_signature = ecdsa.util.sigencode_der(r, s, public_key.curve.order)

     
    print("✅ Signature verified successfully!")

    return jsonify({"status": "success", "message": "Authentication successful"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
