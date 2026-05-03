import csv

from fastapi import APIRouter, HTTPException, Header, status
from typing import Optional
from routes.auth_routes import verify_token
from services.ml_model import threat_model, DATA_FILE

router = APIRouter(prefix="/admin", tags=["Network Threats"])


def verify_admin_access(user: dict) -> bool:
    return user and user.get("role") == "admin"


@router.get("/network-threats")
async def get_network_threats(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = authorization.split(" ")[1]
    user = verify_token(token)

    if not user or not verify_admin_access(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return {
        "network_events": threat_model.get_sample_events(12),
        "model_info": threat_model.get_model_info(),
        "summary": {
            "total_samples": len(threat_model.sample_events),
            "malicious_predicted": len([e for e in threat_model.sample_events if e["predicted_label"] == "MALICIOUS"]),
            "benign_predicted": len([e for e in threat_model.sample_events if e["predicted_label"] == "BENIGN"])
        }
    }


@router.get("/network-dataset")
async def get_network_dataset(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = authorization.split(" ")[1]
    user = verify_token(token)

    if not user or not verify_admin_access(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    with open(DATA_FILE, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames or []
        dataset_rows = [row for _, row in zip(range(15), reader)]

    return {
        "dataset_columns": fieldnames,
        "dataset_rows": dataset_rows,
        "summary": {
            "total_rows": len(threat_model.sample_events),
            "feature_columns": threat_model.get_model_info().get("feature_columns", []),
            "malicious_sample_count": len([row for row in dataset_rows if row.get("label") == "malicious"]),
            "benign_sample_count": len([row for row in dataset_rows if row.get("label") == "benign"])
        }
    }
