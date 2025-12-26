import pyotp
import requests

secret = "MySupersecretKey"

totp = pyotp.TOTP(secret)

while True:
    print(totp.verify(input("Enter your TOTP code: ")))