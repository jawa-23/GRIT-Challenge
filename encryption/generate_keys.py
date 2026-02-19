from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path
import sys


def generate_keys(
    public_key_path,
    private_key_path,
    key_size = 4096,
    overwrite = False
):

    # Safety check: prevent accidental overwrite
    if not overwrite and (public_key_path.exists() or private_key_path.exists()):
        print("Error: Key file(s) already exist.")
        print("Set overwrite as True if you really want to replace them.")
        sys.exit(1)

    # Ensure directories exist
    public_key_path.parent.mkdir(parents=True, exist_ok=True)
    private_key_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    public_key = private_key.public_key()


    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm = serialization.NoEncryption(),
    )

    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Write files
    private_key_path.write_bytes(private_pem)
    public_key_path.write_bytes(public_pem)

    print("Keys generated successfully!")
    print(f"Public key:  {public_key_path}")
    print(f"Private key: {private_key_path}")
    print(f"Key size:    {key_size} bits")

if __name__ == "__main__":
    
    public_key_path = Path("public_key.pem")
    private_key_path = Path("private_key.pem")
    key_size = 2048     # options 2048 3072 4096
    overwrite = False

    generate_keys(
        public_key_path,
        private_key_path,
        key_size,
        overwrite
    )

