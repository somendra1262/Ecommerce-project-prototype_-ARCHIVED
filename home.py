from fastapi import FastAPI
from .admin import router as admin_router
from .register_as_a_vendor import router as request_router
from .register_as_a_customer import router as customer_router
from .vendor import router as vendor_router
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
app=FastAPI()

app.include_router(admin_router)
app.include_router(request_router)
app.include_router(customer_router)
app.include_router(vendor_router)
app.mount("/static",StaticFiles(directory="static"),name="static")
@app.get('/')
async def home():
    f=open("home.html","r")
    page=f.read()
    return HTMLResponse(content=page)

@app.get('/login')
async def loginoptions():
    f=open("login.html","r")
    page=f.read()
    return HTMLResponse(content=page)


@app.get('/register')
async def registrationoptions():
    f=open("registrationoptions.html","r")
    page=f.read()
    return HTMLResponse(content=page)

    
