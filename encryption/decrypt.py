import argparse
import base64
import json
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


def decrypt_file(input_enc, private_key_pem, output_csv):

    private_key = serialization.load_pem_private_key(private_key_pem.read_bytes(), password=None)

    try:
        with open(input_enc, "rb") as f:
            content_enc = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {input_enc}")

    rsa_segment_size = 256 
    
    if len(content_enc) < rsa_segment_size:
        raise ValueError("File is too short to contain a valid encrypted header.")

    encrypted_key = content_enc[:rsa_segment_size]
    encrypted_data = content_enc[rsa_segment_size:]

    try:
        symmetric_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        raise ValueError(f"RSA Decryption failed. (Check if Public/Private keys match): {e}")

    try:
        cipher_suite = Fernet(symmetric_key)
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        output_csv.write_bytes(decrypted_data)
        
    except Exception as e:
        raise ValueError(f"Data Decryption failed (Corrupted file?): {e}")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Decrypt encrypted predictions.")
    parser.add_argument("input_enc", type=Path, help="Path to predictions.csv.enc")
    parser.add_argument("private_key_pem", type=Path, help="Path to private key PEM")
    parser.add_argument("output_csv", type=Path, help="Output decrypted predictions.csv path")
    args = parser.parse_args()

    decrypt_file(args.input_enc, args.private_key_pem, args.output_csv)
    print(f"Decrypted submission written to: {args.output_csv}")

