otp_store = {}

def generate_otp(mobile):
    otp = "123456"
    otp_store[mobile] = otp
    print(f"OTP for {mobile}: {otp}")
    return otp

def verify_otp(mobile, otp):
    return otp_store.get(mobile) == otp

