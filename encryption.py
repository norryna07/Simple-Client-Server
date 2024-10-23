import random

# for getting the keys using Diffie-Hellman Key Exchange
# I find the algorithm here: https://medium.com/@dazimax/how-to-securely-exchange-encryption-decryption-keys-over-a-public-communication-network-27f225af4fdb
prime_number = 257
generator = 11

def get_pair_key():
    """Generate a pair of key for using in encryption.
    Generate a random private key. 
    Use the generator and the prime_number to create a public key.

    Returns:
        (int, int): A pair with the private and public key.
    """
    private = random.randint(0, 1000) # generate the private key
    public = pow(generator, private, prime_number) # create the public key
    return (private, public)

def get_shared_key(my_private, public):
    """Generate the shared key that both the server and the client will use.

    Args:
        my_private (int): the private key of the current user
        public (int): the public key received from the other part

    Returns:
        int: the shared key used for encryption
    """
    shared = pow(public, my_private, prime_number) # generate the shared key
    return shared


def encrypt(input, shift):
    """Encode a vector of bytes using Ceaser encryption

    Args:
        input (bytes): The bytes needed to be encrypted.
        shift (int): The key of the Ceaser encryption
    """
    output = bytearray()
    for byte in input:
        byte_out = (byte + shift) % 256
        output.append(byte_out)
    return bytes(output)

def decrypt(input, shift):
    """Decode a vector of bytes using Caesar encryption

    Args:
        input (bytes): The bytes needed to be decrypted.
        shift (int): The key of the Caesar encryption
    """
    return encrypt(input, -shift)
