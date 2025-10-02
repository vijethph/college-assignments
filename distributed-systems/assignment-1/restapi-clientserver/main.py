from typing import Annotated, Sequence
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import Depends, FastAPI, HTTPException, Query
from contextlib import asynccontextmanager
from constants import SQLITE_URL, USER_NOT_FOUND_MSG

connect_args = {"check_same_thread": False}
engine = create_engine(SQLITE_URL, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

class UserBase(SQLModel):
    first_name: str = Field()
    last_name: str = Field()
    age: int | None = Field(default=None, index=True)
    email: str = Field()

class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    age: int | None = Field(default=None)
    email: str | None = Field(default=None)

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)



@app.get("/healthcheck")
def healthcheck():
    return {"message": "The service is healthy"}

@app.post("/users/", response_model=User)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)) -> User:
    user = User.model_validate(user_data)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/")
def read_users(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> Sequence[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@app.get("/users/{user_id}")
def read_user(user_id: int, session: Session = Depends(get_session)) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MSG)
    return user

@app.patch("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdate, session: Session = Depends(get_session)):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MSG)
    user_data = user_update.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MSG)
    session.delete(user)
    session.commit()
    return {"ok": True}