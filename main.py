from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import random

app = FastAPI()

# ---------------- DATA ----------------
menu = [
    {"id": 1, "name": "Burger", "price": 5},
    {"id": 2, "name": "Pizza", "price": 8},
    {"id": 3, "name": "Coffee", "price": 3}
]

orders = []
reviews = []

# ---------------- AUTH ----------------
ADMIN = {"username": "admin", "password": "1234"}
TOKENS = set()
security = HTTPBearer()

# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: dict):
    if data["username"] == ADMIN["username"] and data["password"] == ADMIN["password"]:
        token = str(random.randint(100000, 999999))
        TOKENS.add(token)
        return {"token": token}

    raise HTTPException(status_code=401, detail="Invalid credentials")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in TOKENS:
        raise HTTPException(status_code=403, detail="Unauthorized")

# ---------------- MENU ----------------
@app.get("/menu")
def get_menu():
    return menu

# ---------------- ORDER ----------------
@app.post("/order")
def create_order(order: dict):
    items = order["items"]
    total = sum(i["price"] for i in items)

    ticket = random.randint(10000, 99999)

    new_order = {
        "items": items,
        "total": total,
        "ticket": ticket
    }

    orders.append(new_order)
    return {"receipt": new_order}

# ---------------- REVIEWS ----------------
@app.post("/review")
def add_review(review: dict):
    reviews.append(review)
    return {"message": "review saved"}

@app.get("/reviews")
def get_reviews(user=Depends(verify_token)):
    return reviews

# ---------------- SIMPLE AI ENDPOINTS ----------------
@app.get("/ai/summary")
def ai_summary():
    return {
        "total_orders": len(orders),
        "total_reviews": len(reviews),
        "system_status": "Healthy"
    }

@app.get("/ai/issues")
def ai_issues():
    return {
        "status": "OK",
        "issues": ["No critical issues detected"]
    }