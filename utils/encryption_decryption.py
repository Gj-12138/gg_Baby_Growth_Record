import base64

from cryptography.fernet import Fernet

# from DjangoProject1.settings import KEY_EMAIL


def get_key():
    return Fernet.generate_key().decode("utf-8")

# Key_Email = get_key()
# print(Key_Email)

def encryption(data,key):
    f = Fernet(key)
    if isinstance(data,str):
        data = data.encode("utf-8")
    encrypted = f.encrypt(data)
    base64_data = base64.urlsafe_b64encode(encrypted).decode("utf-8")
    return base64_data


# print(encryption("123",Key_Email),type(encryption("123",Key_Email)))

def decryption(data,key):
    f = Fernet(key)
    encrypted_data = base64.urlsafe_b64decode(data.encode("utf-8"))
    decrypted_data = f.decrypt(encrypted_data)
    return decrypted_data.decode("utf-8")
