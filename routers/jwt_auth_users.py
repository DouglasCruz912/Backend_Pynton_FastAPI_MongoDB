from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 10
SECRET = "afasdfsgadhstrhbstyatn"

router = APIRouter()

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDB(User):
    password: str


users_db = {
    "douglasdev": {
        "username": "DgS",
        "full_name": "Douglas Jose",
        "email": "douglasjose@gmail.com",
        "disabled": False,
        "password": "$2a$12$RAGxnSVG6sLIoJzlQRjkFumLw0gok74nJLmiWWwXakpH.1OAcqVP6"
    },

    "douglasdev2": {
        "username": "DgS2",
        "full_name": "Douglas Cruz",
        "email": "douglasjose2@gmail.com",
        "disabled": False,
        "password": "$2a$12$gUQftQGKh6nFH1Wrik7HpevKt1FlE9/uwL.OR8RwcZ1jJ8YMYdm3O"
    },
}


def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])

async def auth_user(token: str = Depends(oauth2)):
   
    exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales de autenticación inválidas",
            headers={"wwww-Authenticate": "Bearer"})


    try:
        username = jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")
        if username is None:
            raise exception

    except JWTError:
       raise exception
    

    return search_user(username)

    
async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
       raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Usuario inactivo")
   
    return user


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if not users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no es correcto")
    

    user = search_user_db(form.username)


    if not crypt.verify(form.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="la contraseña no es correcta")
    
    access_token = {"sub": user.username,
                    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}
    
    return {"access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@router.get("/users/me")
async def  me(user:User = Depends(current_user)):
    return user
