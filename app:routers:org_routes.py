from fastapi import APIRouter, HTTPException
from app.database import master_db, client
from app.models import OrgCreate, OrgUpdate
from app.auth import hash_password
from bson.objectid import ObjectId

router = APIRouter(prefix="/org", tags=["org"])

@router.post("/create")
def create_org(data: OrgCreate):
    org_name = data.organization_name.strip().lower()

    # Validate uniqueness
    if master_db.organizations.find_one({"organization_name": org_name}):
        raise HTTPException(status_code=400, detail="Organization already exists")

    # Create dynamic database per org
    db_name = f"org_{org_name}"
    # Touch the DB by creating a tiny collection then removing it
    client[db_name]["_init"].insert_one({"created_at": True})
    client[db_name].drop_collection("_init")

    # Create admin user in master admin collection
    admin_doc = {
        "email": data.email,
        "password": hash_password(data.password)
    }
    inserted = master_db.admins.insert_one(admin_doc)
    admin_id = inserted.inserted_id

    # Save metadata to master organizations collection
    org_meta = {
        "organization_name": org_name,
        "db_name": db_name,
        "admin_id": admin_id
    }
    master_db.organizations.insert_one(org_meta)

    return {"message": "Organization created", "db_name": db_name, "admin_id": str(admin_id)}

@router.get("/get")
def get_org(organization_name: str):
    org = master_db.organizations.find_one({"organization_name": organization_name.strip().lower()})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    org["admin_id"] = str(org["admin_id"])
    org["_id"] = str(org["_id"])
    return org

@router.put("/update")
def update_org(data: OrgUpdate):
    org_name = data.organization_name.strip().lower()
    org = master_db.organizations.find_one({"organization_name": org_name})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    new_db_name = f"{org['db_name']}_v2"

    # create new DB and copy data (basic copy: copy all collections)
    old_db = client[org["db_name"]]
    new_db = client[new_db_name]

    # copy each collection
    for coll_name in old_db.list_collection_names():
        if coll_name.startswith("system."):
            continue
        docs = list(old_db[coll_name].find())
        if docs:
            new_db[coll_name].insert_many(docs)

    # update metadata to point to new db
    master_db.organizations.update_one({"organization_name": org_name}, {"$set": {"db_name": new_db_name}})

    return {"message": "Organization updated", "new_db_name": new_db_name}

@router.delete("/delete")
def delete_org(organization_name: str):
    org = master_db.organizations.find_one({"organization_name": organization_name.strip().lower()})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # delete whole database for the org
    client.drop_database(org["db_name"])

    # delete admin and org metadata
    master_db.organizations.delete_one({"organization_name": organization_name.strip().lower()})
    # Optionally delete admin user
    master_db.admins.delete_one({"_id": org["admin_id"]})

    return {"message": "Organization and associated DB deleted"}
