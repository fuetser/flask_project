from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, constr, Field, root_validator, validator

from ..models import User, Group


class UserLikeModel(BaseModel):
    id: int
    username: constr(max_length=25)
    email: constr(max_length=64)
    registered: datetime = datetime.utcnow()

    class Config:
        orm_mode = True


class CommentModel(BaseModel):
    id: int
    post_id: int
    author_id: int
    timestamp: datetime = datetime.utcnow(),
    body: str
    is_reply: bool = False
    reply_to: Optional[int]
    likes: Optional[List[UserLikeModel]] = []

    class Config:
        orm_mode = True


class PostModelBase(BaseModel):
    title: constr(max_length=64)
    body: str
    timestamp: datetime = datetime.utcnow()
    author_id: int
    group_id: int
    likes: Optional[List[UserLikeModel]] = []
    comments: Optional[List[CommentModel]] = []

    class Config:
        extra = "forbid"


class PostModel(PostModelBase):
    id: int

    class Config:
        orm_mode = True


class PostModelUpdate(BaseModel):
    title: Optional[constr(max_length=64)]
    body: Optional[str]
    timestamp: Optional[datetime]
    author_id: Optional[int]
    group_id: Optional[int]
    likes: Optional[List[UserLikeModel]]
    comments: Optional[List[CommentModel]]

    class Config:
        extra = "forbid"


class PostModelCreate(PostModelBase):
    pass


class UserModelBase(BaseModel):
    username: constr(max_length=25)
    email: constr(max_length=64)
    password_hash: constr(max_length=255) = Field(None, alias="password")
    registered: datetime = datetime.utcnow()
    posts: List[PostModel] = []
    comments: List[CommentModel] = []

    class Config:
        extra = "forbid"


class UserModel(UserModelBase):
    id: int

    class Config:
        orm_mode = True


class UserModelCreate(UserModelBase):
    @root_validator
    def validate_unique_fields(cls, values):
        username = values.get("username")
        email = values.get("email")
        if not User.is_free_username(username):
            raise ValueError(f'Username "{username}" is already taken')
        if not User.is_free_email(email):
            raise ValueError(f'Email "{email}" is already taken')
        return values


class UserModelUpdate(BaseModel):
    username: Optional[constr(max_length=25)]
    email: Optional[constr(max_length=64)]
    password_hash: Optional[constr(max_length=255)] = Field(None, alias="password")
    registered: Optional[datetime]
    posts: Optional[List[PostModel]]
    comments: Optional[List[CommentModel]]

    class Config:
        extra = "forbid"

    @root_validator
    def validate_unique_fields(cls, values):
        username = values.get("username")
        email = values.get("email")
        if not User.is_free_username(username):
            raise ValueError(f'Username "{username}" is already taken')
        if not User.is_free_email(email):
            raise ValueError(f'Email "{email}" is already taken')
        return values


class GroupModelBase(BaseModel):
    name: constr(max_length=32)
    description: constr(max_length=128)
    admin_id: int
    posts: Optional[List[PostModel]] = []
    subscribers: Optional[List[UserModel]] = []

    class Config:
        extra = "forbid"


class GroupModel(GroupModelBase):
    id: int

    class Config:
        orm_mode = True


class GroupModelCreate(GroupModelBase):
    @validator("name")
    def check_unique_name(cls, value):
        if not Group.is_unique_name(value):
            raise ValueError(f'Group name "{value}" is already taken')
        return value


class GroupModelUpdate(GroupModelBase):
    name: Optional[constr(max_length=32)]
    description: Optional[constr(max_length=128)]
    admin_id: Optional[int]

    class Config:
        extra = "forbid"


class TokenCreateModel(BaseModel):
    username: constr(max_length=25)
    password: constr(max_length=128)

    class Config:
        extra = "forbid"
