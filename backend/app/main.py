from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI instance
app = FastAPI(
    title = "Astro AI API",
    description = "Astro assistant backend API for status and 2D states",
    version = "0.1.0",
)

#Configure CORS Middleware (connection allowed between backend port and frontend port)
origins = ["http://localhost:5173", 
           "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of allowed origins for CORS
    allow_credentials=True, # Allow credentials (cookies, authorization headers, etc.)
    allow_methods=["*"], # Allow all HTTP methods
    allow_headers=["*"], # Allow all headers
)

#first route decorator
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the Astro AI Assistant API",
        "version": "0.1.0"
    }




# @app.get binds HTTP GET requests targeting the '/health' URL to this function
@app.get("/health", tags=["Health System Check"])
async def health_check():
    '''
    Health check endpoint to verify the API is running.
    Returns a JSON response indicating the API status.
    '''
    return {
        "status": "online",
        "message": "Astro API is online and running smoothly."
    }





