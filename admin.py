from fastapi.responses import HTMLResponse,RedirectResponse
import redis
from . import database_interface as db
import secrets
from datetime import datetime,timedelta,UTC
from . import send_mail_interface as sendotp
from fastapi import APIRouter,Cookie,Form,HTTPException,Request
from fastapi.responses import HTMLResponse
from . import token_creation_and_validation as jwt
from typing import Annotated
from fastapi.templating import Jinja2Templates
ADMIN_EMAIL="somendrasingh1262@gmail.com"
ADMIN_PASSWORD="89U3WP8UAFUWR4&(^*8F9WAU9F8EJ"

router=APIRouter(tags=["admin_router"])
templates=Jinja2Templates(directory=".")

@router.post('/restricted/create_otp')
async def create_and_sendotp(email:Annotated[str,Form()],password:Annotated[str,Form()]):
    if(email!=ADMIN_EMAIL or password!=ADMIN_PASSWORD):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    sendotp.sendmail(email)

    f=open("enterotpadmin.html")
    page=f.read()
    response=HTMLResponse(page)
    expiry=datetime.now(UTC)+timedelta(minutes=60)
    token=jwt.create_jwt({"sub":email,"exp":int(expiry.timestamp())})
    response.set_cookie(key="auth_token",value=token,path="/restricted/verify",httponly=True,samesite="lax")

    return response

@router.post('/restricted/verify')
async def verifyotp(otp:Annotated[str,Form()],auth_token:Annotated[str,Cookie()]):
    try:
        jwt.verify_jwt(auth_token)
    except ValueError:
        return {"error":"auth token has been expired or tampered with"}
    r=redis.Redis(host="localhost", port=6379,db=0,decode_responses=True)
    if r.get(otp)==None:
        return {"error":"otp expired or not found"}
    e=r.get(otp)
    if e!=ADMIN_EMAIL:
        return {"error":"invalid otp"}
    response=RedirectResponse(url="/a0",status_code=303)
    response.set_cookie(key="auth_token",value=auth_token,path="/a0",httponly=True,samesite="lax")
    return response

@router.post('/a0/approve_or_reject')
async def delete_or_insert(email:Annotated[str,Form()],button:Annotated[str,Form()],auth_token:Annotated[str,Cookie()]):
    try:
        jwt.verify_jwt(auth_token)
    except ValueError:
        return {"error":"auth token has been expired or tampered with"}
    if button=="reject":
        db.delete_vr(email)
    else:
        db.insert_v(email)
        db.delete_vr(email)
    return RedirectResponse(url="/a0/pending",status_code=303)

@router.get('/restricted')
async def adminlogin():
    f=open("adminlogin.html")
    page=f.read()
    return HTMLResponse(page)


@router.get('/a0/pending')
async def pending(request:Request, auth_token:Annotated[str,Cookie()]):
    try:
        jwt.verify_jwt(auth_token)
    except ValueError:
        return {"error":"auth token has been expired or tampered with"}
    l=db.select_allvr()
    page=templates.TemplateResponse(name="pending.html",request=request,context={"pending_requests":l})
    return page

@router.get('/a0')
async def welcometothedashboard(auth_token:Annotated[str,Cookie()]):
    try:
        jwt.verify_jwt(auth_token)
    except ValueError:
        return {"error":"auth token has been expired or tampered with"}
    f=open("admindashboard.html","r")
    page=f.read()
    return HTMLResponse(page)
