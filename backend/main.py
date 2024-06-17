from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import firebase_admin
from firebase_admin import credentials, firestore
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import logging

# Initialize FastAPI app
app = FastAPI()

# Initialize Firebase Admin SDK
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define a function to fetch specific fields from Firestore document
def fetch_fields(doc):
    # Extract specific fields from the Firestore document
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
    
# Define a function to fetch specific fields from Firestore document
def fetch_lon_lat(doc):
    # Extract 'long' and 'lat' fields from the Firestore document
    return {
        'place_id': doc.id,
        'name': doc.get('name'),
        'lat': doc.get('lat'),
        'long': doc.get('long')        
    }
    
# Mount the static files directory
app.mount("/img", StaticFiles(directory="img"), name="img")

@app.get("/")
def read_root():
    return {"REST API for Journey on Solo"}

@app.get("/data")
async def get_data():
    try:
        collection_ref = db.collection('location')
        docs = collection_ref.stream()
        
        # Initialize an empty list to store formatted data
        formatted_data = []
        
        # Iterate over documents and format each one
        for doc in docs:
            data = fetch_fields(doc)
            formatted_data.append(data)
            
        return formatted_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint display detail
@app.get("/data/{place_id}")
async def get_detail_data(place_id: str):
    try:
        # Fetch data from Firestore
        collection_ref = db.collection('location')
        query_ref = collection_ref.where('place_id', '==', place_id).limit(1).get()
        for doc in query_ref:
            data = fetch_fields(doc)
            # Add the image URL to the response
            # data['image_url'] = f"34.101.153.83:3000/img/{place_id}.jpg"
            return data
        raise HTTPException(status_code=404, detail=f"Document with place_id '{place_id}' not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to fetch all 'lon' and 'lat'
@app.get("/coordinates")
async def get_all_coordinates():
    try:
        collection_ref = db.collection('location')
        docs = collection_ref.stream()
        
        # Initialize an empty list to store long and lat data
        coordinates = []
        
        # Iterate over documents and fetch long and lat
        for doc in docs:
            data = fetch_lon_lat(doc)
            coordinates.append(data)
            
        return coordinates

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Endpoint to fetch only 'long' and 'lat' by place_id
@app.get("/coordinates/{place_id}")
async def get_coordinates(place_id: str):
    try:
        collection_ref = db.collection('location')
        
        # Query Firestore for documents where 'place_id' matches
        query_ref = collection_ref.where('place_id', '==', place_id).limit(1).get()
        
        # Check if any documents match the query
        for doc in query_ref:
            # Fetch only 'long' and 'lat' fields
            data = fetch_lon_lat(doc)
            return data
        
        # If no document found with the given place_id
        raise HTTPException(status_code=404, detail=f"Document with place_id '{place_id}' not found")
    
    except HTTPException:
        # Propagate HTTP exceptions (e.g., 404) as they are
        raise
    
    except Exception as e:
        # Handle other exceptions with a generic 500 Internal Server Error
        raise HTTPException(status_code=500, detail=str(e))



# New endpoint for search functionality
@app.get("/search")
async def search_data(
    name: Optional[str] = Query(None, description="Name to search for"),
):
    try:
        # Log the query parameter
        logging.debug(f"Search query parameter: name='{name}'")

        collection_ref = db.collection('location')  # Ensure you are querying the correct collection
        query = collection_ref
        
        if name:
            query = query.where('name', '==', name)
        
        docs = query.stream()
        
        # Convert to list and log the raw documents fetched
        raw_docs = list(docs)
        logging.debug(f"Raw documents fetched: {raw_docs}")
        
        results = []
        
        for doc in raw_docs:
            data = fetch_fields(doc)
            results.append(data)
        
        logging.debug(f"Search results: {results}")
        
        if not results:
            logging.debug("No documents matched the query.")
        
        return results

    except Exception as e:
        logging.error(f"Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))