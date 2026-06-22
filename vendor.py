from . import database_interface as db
from . import send_mail_interface
from fastapi import APIRouter,Cookie,Form,HTTPException
from fastapi.responses import HTMLResponse,RedirectResponse
from typing import Annotated
from datetime import datetime,timedelta,UTC
import redis
from . import token_creation_and_validation as jwt

router=APIRouter(tags=["vendor_router"])


@router.get('/v0')
async def homev(auth_token:Annotated[str,Cookie()]):
    try:
        jwt.verify_jwt(auth_token)
    except ValueError:
        return {"error":"auth token has been expired or tampered with"}
    f=open("homev.html","r")
    page=f.read()
    return HTMLResponse(page)

@router.get('/v0/enter_details')
async def upload_page(auth_token:Annotated[str,Cookie()]):
    try:
        payload=jwt.verify_jwt(auth_token)
    except ValueError:
        return {"error":"auth token has been expired or tampered with"}
    f=open("upload_product.html","r")
    page=f.read()
    return HTMLResponse(page)

@router.post('/v0/upload_product')
async def upload(auth_token:Annotated[str,Cookie()],pname:Annotated[str,Form()],pdesc:Annotated[str,Form()],pimg:Annotated[str,Form()],pcategory:Annotated[str,Form()],price:Annotated[str,Form()],quantity:Annotated[str,Form()]):
    try:
        payload=jwt.verify_jwt(auth_token)
    except ValueError:
        return {"error":"auth token has been expired or tampered with"}
    l=db.select_allv()
    found=False
    for i in l:
        if i[0]==payload["sub"]:
            found=True
    if found==False:
        raise HTTPException(status_code=401, detail="Your account has been removed, contact the administrator for details: somendrasingh1262@gmail.com")
    data = {
    "name": pname,
    "image": pimg,
    "desc": pdesc,
    "category": pcategory,
    "email":payload["sub"],
    "price":price,
    "quantity":quantity}
    db.insert_p(data)
    return RedirectResponse(url='/v0/enter_details', status_code=303)


@router.post('/vendor_login/check_and_sendotp')
async def sendotpv(email:Annotated[str,Form()],password:Annotated[str,Form()]):
    l=db.select_allv()
    found=False
    for i in l:
        if i[0]==email:
            if i[1]==password:
                found=True
    if(found==False):
        return {"error":"your vendor account was not found"}
    send_mail_interface.sendmail(email)
    f=open("enterotpv.html","r")
    page=f.read()
    response=HTMLResponse(page)
    expiry=datetime.now(UTC)+timedelta(minutes=60)
    token=jwt.create_jwt({"sub":email,"exp":int(expiry.timestamp())})
    response.set_cookie(key="auth_token",value=token,path="/vendor_login/enterotp",httponly=True,samesite="lax")
    return response

@router.post('/vendor_login/enterotp')
async def verifyotpv(otp:Annotated[str,Form()],auth_token:Annotated[str,Cookie()]):
    try:
        payload=jwt.verify_jwt(auth_token)
    except ValueError:
        return {"error":"auth token has been expired or tampered with"}
    r=redis.Redis(host="localhost", port=6379,db=0,decode_responses=True)
    if r.get(otp)==None:
        return {"error":"otp expired or not found"}
    e=r.get(otp)
    if e==None or e!=payload["sub"]:
        return {"error":"invalid otp"}
    response=RedirectResponse(url="/v0",status_code=303)
    response.set_cookie(key="auth_token",value=auth_token,path="/v0",httponly=True,samesite="lax")
    return response

@router.get('/vendor_login')
async def loginpage():
    f=open("vendor_login.html","r")
    page=f.read()
    return HTMLResponse(page)
