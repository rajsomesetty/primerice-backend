from pydantic import BaseModel

class SignupRequest(BaseModel):
    name: str
    mobile: str
    password: str

class LoginRequest(BaseModel):
    mobile: str
    password: str

class AddressCreate(BaseModel):
    name: str
    mobile: str
    address_line: str
    city: str
    pincode: str
