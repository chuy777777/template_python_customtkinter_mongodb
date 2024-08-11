from __future__ import annotations

from bson import ObjectId

class User():
    def __init__(self, _id, name):
        self._id: ObjectId=_id
        self.name: str=name

    def to_json(self):
        return {
            "_id": self._id,
            "name": self.name,
        }

    @staticmethod
    def from_json(obj):
        return User(
            _id=obj["_id"],
            name=obj["name"],
        )

    @staticmethod
    def get_empty():
        obj={
            "_id": ObjectId(),
            "name": "",
        }
        return User.from_json(obj=obj)

