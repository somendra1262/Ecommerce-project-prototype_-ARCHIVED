from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel,Field, Session, select, delete
import asyncio
import base64


class vendor_request(SQLModel, table=True):
    email:str=Field(primary_key=True)
    password:str
    brandname:str
    address:str
    category:str

class customer(SQLModel,table=True):
    email:str=Field(primary_key=True)
    password:str

class vendor(SQLModel, table=True):
    email:str=Field(primary_key=True)
    password:str
    brandname:str
    address:str
    category:str
    avgr:float|None

class product(SQLModel,table=True):
    pid:int|None=Field(default=None, primary_key=True)
    email:str
    name:str
    category:str
    price:int
    quantity:int
    image:bytes
    desc:str
    avgr_p:float|None

class review(SQLModel, table=True):
    rid:int|None=Field(default=None,primary_key=True)
    desc:str|None
    rating:float
    pid:int

engine=create_async_engine("postgresql+asyncpg://postgres:toasted@127.0.0.1:5432/postgres",echo=True)
async def create_tables():
    async with engine.begin() as con:
        await con.run_sync(SQLModel.metadata.create_all)

asyncSession=async_sessionmaker(bind=engine, expire_on_commit=False)


async def insert_vr(data:dict):
    entity=vendor_request(**data)
    async with asyncSession() as session:
        session.add(entity)
        await session.commit()

async def delete_vr(key:str):
    async with asyncSession() as session:
        query=select(vendor_request).where(vendor_request.email==key)
        to_delete=await session.execute(query)
        to_delete=to_delete.scalar_one()
        await session.delete(to_delete)
        await session.commit()

async def select_allvr():
    async with asyncSession() as session:
        statement=select(vendor_request)
        results=await session.execute(statement)
        results=results.scalars()
        l=[]
        for i in results:
            l.append([i.email,i.password,i.brandname,i.address,i.category])
        return l

async def select_allv():
    async with asyncSession() as session:
        statement=select(vendor)
        results=await session.execute(statement)
        results=results.scalars()
        l=[]
        for i in results:
            l.append([i.email,i.password,i.brandname,i.address,i.category])
        return l

async def insert_c(data:dict):
    entity=customer(**data)
    async with asyncSession() as session:
        session.add(entity)
        await session.commit()

async def delete_c(email:str):
    async with asyncSession() as session:
        query=select(customer).where(customer.email==email)
        to_delete= await session.execute(query)
        to_delete=to_delete.scalar_one()
        await session.delete(to_delete)
        await session.commit()


async def insert_v(key:str):
    async with asyncSession() as session:
        query=select(vendor_request).where(vendor_request.email==key)
        to_insert=await session.execute(query)
        to_insert=to_insert.scalar_one()
        vend=vendor(email=to_insert.email,password=to_insert.password,brandname=to_insert.brandname,address=to_insert.address,category=to_insert.category)
        session.add(vend)
        await session.commit()


async def delete_v(key:str):
    async with asyncSession() as session:
        query=select(vendor).where(vendor.email==key)
        to_delete= await session.execute(query)
        to_delete=to_delete.scalar_one()
        await session.delete(to_delete)
        await session.commit()

async def insert_p(data:dict):
    entity=product(**data)
    async with asyncSession() as session:
        session.add(entity)
        await session.commit()


async def select_p(e:str):
    async with asyncSession() as session:
        query=select(product).where(product.email==e)
        results = await session.execute(query)
        results = results.scalars()
        l=[]
        for i in results:
            image=base64.b64encode(i.image).decode('utf-8')
            l.append([i.pid, i.name, image, i.price, i.quantity, i.category, i.desc, i.avgr_p])
        return l

async def select_v(e:str):
    async with asyncSession() as session:
        query=select(vendor).where(vendor.email==e)
        obj= await session.execute(query)
        obj=obj.scalars()
        l=[]
        for i in obj:
            l.append(i)
        return l 

async def truncateall():
    async with asyncSession() as session:
        query=delete(vendor)
        query2=delete(vendor_request)
        query3=delete(customer)
        query4=delete(product)
        await session.execute(query)
        await session.execute(query2)
        await session.execute(query3)
        await session.execute(query4)
        await session.commit()

async def reset_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

async def insert_r(rev:dict):
    obj=review(**rev)
    async with asyncSession() as session:
        session.add(obj)
        await session.commit()

async def delete_r(x:int):
    async with asyncSession() as session:

        query=select(review).where(review.rid==x)
        to_delete=await session.execute(query)
        to_delete=to_delete.scalar_one()
        await session.delete(to_delete)
        await session.commit()

async def select_allr():
    async with asyncSession() as session:
        query=select(review)
        obj=await session.execute(query)
        obj=obj.scalars()
        l=[]
        for i in obj:
            l.append([i.rid,i.desc,i.rating,i.pid])
        print(l)


async def m():
    await select_allr()




asyncio.run(m())
