from fastapi import APIRouter,Form,Cookie
from fastapi.responses import HTMLResponse,RedirectResponse
from typing import Annotated
from datetime import datetime,timezone,timedelta
import secrets
import mailtrap as m
from . import database_interface as db
import redis

router=APIRouter(tags=["request_router"])
@router.post('/register_as_a_vendor/create_otp')
async def sendmail(email:Annotated[str,Form()],password:Annotated[str,Form()],brandname:Annotated[str,Form()],address:Annotated[str,Form()],category:Annotated[str,Form()]):
    d={"email":email,"password":password,"brandname":brandname,"address":address,"category":category}
    db.insert_vr(d)
    r=redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)
    otp="".join(secrets.choice("0123456789") for i in range(6))
    mail=m.Mail(sender=m.Address(email="toad@demomailtrap.co"),to=[m.Address(email=email)],subject="One time password for vendor registration request",text="here is your one time password (otp): "+otp,category="one time password",)
    client=m.MailtrapClient(token="38ee6d5aa1e829263fec56292cccbe11")
    client.send(mail)
    r.set(email,otp,ex=60)
    f=open("enterotp.html")
    page=f.read()
    response=HTMLResponse(page)
    response.set_cookie(key="email",value=email,httponly=True,samesite="lax",path="/register_as_a_vendor/success")
    return response

@router.post('/register_as_a_vendor/success')
async def verifyotp(otp:Annotated[str,Form()],email:Annotated[str,Cookie()]):
    r=redis.Redis(host="localhost", port=6379,db=0,decode_responses=True)
    if not r.get(email):
        db.delete_vr(email)
        raise HTTPException(status_code=400, detail="OTP expired or not found")
    if r.get(email) != otp:
        db.delete_vr(email)
        raise HTTPException(status_code=400, detail="Invalid OTP")
    r.delete(email)
    f=open("vrsuccess.html")
    page=f.read()
    return HTMLResponse(page)
    



@router.get('/register_as_a_vendor')
async def form():
    f=open("register_as_a_vendor.html","r")
    page=f.read()
    return HTMLResponse(page)



