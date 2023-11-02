from fastapi import Depends, FastAPI

from expenses.api.routers import (
    database_router,
    expenses_router,
    merchants_router,
    monitoring_router,
)
from expenses.api.security import check_access_token

# Define the FastAPI app
app = FastAPI(title="Personal expenses API", version="0.1.0")


# Create a root endpoint
@app.get("/", dependencies=[Depends(check_access_token)])
async def root():
    return {"message": "Caaosorioal API for personal expenses"}


# Add the routers
app.include_router(expenses_router, tags=["Expenses"])
app.include_router(database_router, tags=["Database"])
app.include_router(merchants_router, tags=["Merchants"])
app.include_router(monitoring_router, tags=["Monitoring"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("expenses.main:app", host="0.0.0.0", port=5000, reload=True)
