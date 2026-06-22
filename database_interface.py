from sqlmodel import Field, Session, SQLModel, create_engine, insert, select

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

class product(SQLModel,table=True):
    pid:int|None=Field(default=None, primary_key=True)
    email:str
    name:str
    category:str
    price:int
    quantity:int
    image:bytes
    desc:str

engine=create_engine("sqlite:///myecomdb.db",echo=True)
SQLModel.metadata.create_all(engine)

def insert_vr(data:dict):
    entity=vendor_request(**data)
    with Session(engine) as session:
        session.add(entity)
        session.commit()
def delete_vr(key:str):
    with Session(engine) as session:
        query=select(vendor_request).where(vendor_request.email==key)
        to_delete=session.exec(query).one()
        session.delete(to_delete)
        session.commit()

def select_allvr():
    with Session(engine) as session:
        statement=select(vendor_request)
        results=session.exec(statement)
        l=[]
        for i in results:
            l.append([i.email,i.password,i.brandname,i.address,i.category])
        return l

def select_allv():
    with Session(engine) as session:
        statement=select(vendor)
        results=session.exec(statement)
        l=[]
        for i in results:
            l.append([i.email,i.password,i.brandname,i.address,i.category])
        return l

def insert_c(data:dict):
    entity=customer(**data)
    with Session(engine) as session:
        session.add(entity)
        session.commit()

def delete_c(email:str):
    with Session(engine) as session:
        query=select(customer).where(customer.email==email)
        to_delete=session.exec(query).one()
        session.delete(to_delete)
        session.commit()


def insert_v(key:str):
    with Session(engine) as session:
        query=select(vendor_request).where(vendor_request.email==key)
        to_insert=session.exec(query).one()
        vend=vendor(email=to_insert.email,password=to_insert.password,brandname=to_insert.brandname,address=to_insert.address,category=to_insert.category)
        session.add(vend)
        session.commit()


def delete_v(key:str):
    with Session(engine) as session:
        query=select(vendor).where(vendor.email==key)
        to_delete=session.exec(query).one()
        session.delete(to_delete)
        session.commit()

def insert_p(data:dict):
    entity=product(**data)
    with Session(engine) as session:
        session.add(entity)
        session.commit()



