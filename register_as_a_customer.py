from fastapi import APIRouter,Depends,Cookie,Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
import json
from typing import Annotated
from datetime import datetime,timedelta,UTC
import base64,json,hmac,hashlib
import random
from . import token_creation_and_validation as jwt
import redis
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
from . import database_interface as db
KEY=b"ifaoejfi124osfjiashofsi"
router=APIRouter(tags=["customer_router"])
@router.post('/register_as_a_customer/create_otp')
async def sendotp(email:Annotated[str,Form()],password:Annotated[str,Form()]):
    otp="".join(secrets.choice("0123456789") for i in range(6))

    mail=MIMEMultipart()
    mail["From"]="singhsavi333@gmail.com"
    mail["To"]=email
    mail["Subject"]="Your one time password"
    mail.attach(MIMEText(f"Your OTP for registering is: {otp}","plain"))
    smtpserver=smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.starttls()
    smtpserver.login(mail["From"],"olej xwui swyc ayes")
    smtpserver.sendmail(mail["From"],mail["To"],mail.as_string())

    smtpserver.quit()
    r=redis.Redis(host="localhost", port=6379,db=0,decode_responses=True)
    r.set(otp,json.dumps({"email":email,"password":password}),ex=300)


    f=open("enterotpcustomer.html")
    page=f.read()
    response=HTMLResponse(page)
    expiry=datetime.now(UTC)+timedelta(minutes=60)
    token=jwt.create_jwt({"sub":email,"exp":int(expiry.timestamp())})
    response.set_cookie(key="auth_token",value=token,path="/register_as_a_customer/success",httponly=True,samesite="lax")
    response.set_cookie(key="email",value=email,path="/register_as_a_customer/success",httponly=True,samesite="lax")
    return response

@router.post('/register_as_a_customer/success')
async def verify(auth_token:Annotated[str,Cookie()],email:Annotated[str,Cookie()],otp:Annotated[str,Form()]):
    
    try:
        jwt.verify_jwt(auth_token)
    except ValueError:
        return {"error":"auth token has been expired or tampered with"}

    r=redis.Redis(host="localhost", port=6379,db=0,decode_responses=True)
    if r.get(otp)==None:
        return {"error":"OTP expired or not found"}
    user=json.loads(r.get(otp))
    if user["email"]!=email:
        return {"error":"Invalid OTP"}
    db.insert_c(user)
    response=RedirectResponse(url="/u0",status_code=303)
    response.set_cookie(key="auth_token",value=auth_token,path="/u0",httponly=True,samesite="lax")
    return response


@router.get('/register_as_a_customer')
async def form():
    f=open("register_as_a_cust.html","r")
    page=f.read()
    return HTMLResponse(page)

@router.get('/u0')
async def welcome(auth_token:Annotated[str,Cookie()]):
    try:
        jwt.verify_jwt(auth_token)
    except ValueError:
        return {"error":"auth token has been expired or tampered with"}
    f=open("home.html","r")
    page=f.read()
    return HTMLResponse(page)
 
