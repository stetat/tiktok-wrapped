from fastapi import FastAPI, responses, Depends, UploadFile, HTTPException
from io import BytesIO

from zipfile import ZipFile
from datetime import datetime, date
from typing import Union, Annotated
from contextlib import asynccontextmanager
from sqlmodel import Field, Session, SQLModel, create_engine, select
import json

class Users(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(unique=True)
    username: Union[str, None] = None
    requests: int = 0
    user_since: datetime = Field(default_factory=date.today)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App has started")
    create_db_and_tables()
    yield
    print("App has stopped")


app = FastAPI(lifespan=lifespan)



@app.post("/users/new/")
async def new_user(user_id: int, username: str, session: SessionDep):
    exists = session.scalar(select(Users).where(Users.user_id == user_id))

    if not exists:
        newUser = Users(user_id=user_id, username=username)
        session.add(newUser)
        session.commit()

    return responses.JSONResponse(content=f"User {user_id} has been added")

@app.post("/users/new_request/")
async def new_request(user_id: int, session: SessionDep):
    user = session.exec(select(Users).where(Users.user_id==user_id)).one()
    user.requests += 1
    session.commit()
    session.refresh(user)

    return responses.JSONResponse(content=f"User {user_id} has made a new request")



@app.post("/tiktok_wrapped/zip/")
async def get_stats(file: UploadFile):
    contents = await file.read()
    watchCount = 0
    likeCount = 0
    shareCount = 0

    try:
        with ZipFile(BytesIO(contents), 'r') as zFile:
            with zFile.open('user_data_tiktok.json', 'r') as jsonData:
                allData = json.load(jsonData)
                watchCount = len(allData['Your Activity']['Watch History']['VideoList'])
                likeCount = len(allData['Your Activity']['Like List']['ItemFavoriteList'])
                shareCount = len(allData['Your Activity']['Share History']['ShareHistoryList'])

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File can't be read")

    return {"total_watched": watchCount,
            "total_liked": likeCount,
            "total_shared": shareCount}





