from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth_routes, admin_routes, schemes_routes, ai_routes, weather_routes, advisory_routes, farmer_routes

app = FastAPI(title="AgroAssist API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Auth"])
app.include_router(farmer_routes.router, prefix="/api", tags=["Farmer"])
app.include_router(admin_routes.router, prefix="/api/admin", tags=["Admin"])
app.include_router(schemes_routes.router, prefix="/api/schemes", tags=["Schemes"])
app.include_router(ai_routes.router, prefix="/api/ai", tags=["AI Chat"])
app.include_router(weather_routes.router, prefix="/api/weather", tags=["Weather"])
app.include_router(advisory_routes.router, prefix="/api/advisory", tags=["Advisory"])

@app.get("/")
async def root():
    return {"message": "Welcome to AgroAssist API"}
