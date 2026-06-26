from bson import ObjectId

def serialize(doc: dict) -> dict:
    """Convierte _id de ObjectId a string para serializar como JSON."""
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

def serialize_list(docs) -> list:
    return [serialize(d) for d in docs]
