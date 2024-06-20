from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from firebase_admin import credentials, auth, initialize_app, firestore
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging
import httpx
import os

# Initialize FastAPI app
app = FastAPI()

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Models
class User(BaseModel):
    username: str
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    message: str
    token: str = None
    error: str = None

class LoginResponse(BaseModel):
    error: bool
    message: str
    loginResult: dict = None

class UserDetail(BaseModel):
    username: str
    email: str
    password: str

class Place(BaseModel):
    place_id: str
    name: str
    rating: float = None
    reviews_count: int = None
    address: str = None
    lat: float
    long: float
    category: str = None
    image_url: str = None
    caption_idn: str = None
    caption_eng: str = None

class PlaceCoordinates(BaseModel):
    place_id: str
    name: str
    lat: float
    long: float

# Utility functions
def fetch_fields(doc):
    return {
        'place_id': doc.id,
        'name': doc.get('name'),
        'rating': doc.get('rating'),
        'reviews_count': doc.get('reviews_count'),
        'address': doc.get('address'),
        'lat': doc.get('lat'),
        'long': doc.get('long'),
        'category': doc.get('category'),
        'image_url': f"http://34.101.153.83:3000/img/{doc.id}.jpg",
        'caption_idn': doc.get('caption_idn'),
        'caption_eng': doc.get('caption_eng')
    }

def fetch_lon_lat(doc):
    return {
        'place_id': doc.id,
        'name': doc.get('name'),
        'lat': doc.get('lat'),
        'long': doc.get('long')
    }

# Mount the static files directory
app.mount("/img", StaticFiles(directory="img"), name="img")

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "REST API for Journey on Solo"}

# Endpoint Sign-Up
@app.post("/signup", response_model=AuthResponse)
async def signup(user: User):
    try:
        # Ensure username is unique
        user_ref = db.collection('users').document(user.username)
        if user_ref.get().exists:
            raise HTTPException(status_code=400, detail={"message": "Signup failed", "error": "Username already exists"})
        
        user_record = auth.create_user(
            email=user.email,
            password=user.password,
            email_verified=False,
            disabled=False
        )
        # Save additional user data in Firestore with username as document ID
        user_data = {
            "username": user.username,
            "email": user.email,
            "password": user.password  
        }
        user_ref.set(user_data)
        
        return AuthResponse(message="Signup successful", token=user_record.uid)
    except auth.EmailAlreadyExistsError:
        raise HTTPException(status_code=400, detail={"message": "Signup failed", "error": "Email already exists"})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": "Signup failed", "error": str(e)})

# Endpoint Login
@app.post("/login", response_model=LoginResponse)
async def login(login_user: LoginUser):
    try:
        api_key = os.getenv("FIREBASE_API_KEY", "AIzaSyDxCpXsq-ZSEVHKXqZgO-059JaALp9mXWY")  # Replace with your API Key
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={
                "email": login_user.email,
                "password": login_user.password,
                "returnSecureToken": True
            })

        if response.status_code != 200:
            error_message = response.json().get("error", {}).get("message", "Unknown error")
            raise HTTPException(status_code=400, detail={"message": "Login failed", "error": error_message})

        id_token = response.json().get("idToken")

        # Fetch user details from Firestore
        user_ref = db.collection('users').where('email', '==', login_user.email).stream()
        user_data = None
        for doc in user_ref:
            user_data = doc.to_dict()
            break

        if user_data is None:
            raise HTTPException(status_code=400, detail={"message": "Login failed", "error": "User not found in Firestore"})

        login_result = {
            "username": user_data['username'],
            "email": user_data['email'],
            "token": id_token
        }

        return LoginResponse(error=False, message="success", loginResult=login_result)
    except Exception as e:
        raise HTTPException(status_code=400, detail={"message": "Login failed", "error": str(e)})

# Endpoint to get user details
@app.get("/user/{username}", response_model=UserDetail)
async def get_user_details(username: str):
    try:
        doc_ref = db.collection('users').document(username)
        doc = doc_ref.get()
        if doc.exists:
            user_data = doc.to_dict()
            return UserDetail(username=user_data['username'], email=user_data['email'], password=user_data['password'])
        raise HTTPException(status_code=404, detail=f"User with username '{username}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Firestore data endpoints
@app.get("/data", response_model=list[Place])
async def get_data():
    try:
        collection_ref = db.collection('location')
        docs = collection_ref.stream()
        formatted_data = [fetch_fields(doc) for doc in docs]
        return formatted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/{place_id}", response_model=Place)
async def get_detail_data(place_id: str):
    try:
        doc_ref = db.collection('location').document(place_id)
        doc = doc_ref.get()
        if doc.exists:
            return fetch_fields(doc)
        raise HTTPException(status_code=404, detail=f"Document with place_id '{place_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/coordinates", response_model=list[PlaceCoordinates])
async def get_all_coordinates():
    try:
        collection_ref = db.collection('location')
        docs = collection_ref.stream()
        coordinates = [fetch_lon_lat(doc) for doc in docs]
        return coordinates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/coordinates/{place_id}", response_model=PlaceCoordinates)
async def get_coordinates(place_id: str):
    try:
        doc_ref = db.collection('location').document(place_id)
        doc = doc_ref.get()
        if doc.exists:
            return fetch_lon_lat(doc)
        raise HTTPException(status_code=404, detail=f"Document with place_id '{place_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
