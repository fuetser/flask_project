import datetime
from typing import Optional, List

from pydantic import BaseModel, constr, ConfigDict, Field, field_validator, model_validator

from ..models import User, Group


class UserLikeModel(BaseModel):
    model_config: ConfigDict = ConfigDict(from_attributes=True)

    id: int
    username: constr(max_length=25)
    email: constr(max_length=64)
    registered: datetime.datetime = datetime.datetime.now(datetime.UTC)


class CommentModel(BaseModel):
    model_config: ConfigDict = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    author_id: int
    timestamp: datetime.datetime = datetime.datetime.now(datetime.UTC)
    body: str
    likes: Optional[List[UserLikeModel]] = []


class PostModelBase(BaseModel):
    model_config: ConfigDict = ConfigDict(extra="forbid", from_attributes=True)

    title: constr(max_length=64)
    body: str
    timestamp: datetime.datetime = datetime.datetime.now(datetime.UTC)
    author_id: int
    group_id: int
    likes: Optional[List[UserLikeModel]] = []
    comments: Optional[List[CommentModel]] = []


class PostModel(PostModelBase):
    id: int


class PostModelUpdate(BaseModel):
    model_config: ConfigDict = ConfigDict(extra="forbid")

    title: Optional[constr(max_length=64)]
    body: Optional[str]
    timestamp: Optional[datetime.datetime]
    author_id: Optional[int]
    group_id: Optional[int]
    likes: Optional[List[UserLikeModel]]
    comments: Optional[List[CommentModel]]


class PostModelCreate(PostModelBase):
    pass


class UserModelBase(BaseModel):
    model_config: ConfigDict = ConfigDict(extra="forbid", from_attributes=True)

    username: constr(max_length=25)
    email: constr(max_length=64)
    password_hash: constr(max_length=255) = Field(None, alias="password")
    registered: datetime.datetime = datetime.datetime.now(datetime.UTC)
    posts: List[PostModel] = []
    comments: List[CommentModel] = []


class UserModel(UserModelBase):
    id: int


class UserModelCreate(UserModelBase):
    @model_validator(mode="after")
    @classmethod
    def validate_unique_fields(cls, values):
        username = values.get("username")
        email = values.get("email")
        if not User.is_free_username(username):
            raise ValueError(f'Username "{username}" is already taken')
        if not User.is_free_email(email):
            raise ValueError(f'Email "{email}" is already taken')
        return values


class UserModelUpdate(BaseModel):
    model_config: ConfigDict = ConfigDict(extra="forbid")

    username: Optional[constr(max_length=25)]
    email: Optional[constr(max_length=64)]
    password_hash: Optional[constr(max_length=255)] = Field(
        None, alias="password"
    )
    registered: Optional[datetime.datetime]
    posts: Optional[List[PostModel]]
    comments: Optional[List[CommentModel]]

    @model_validator(mode="after")
    @classmethod
    def validate_unique_fields(cls, values):
        username = values.get("username")
        email = values.get("email")
        if not User.is_free_username(username):
            raise ValueError(f'Username "{username}" is already taken')
        if not User.is_free_email(email):
            raise ValueError(f'Email "{email}" is already taken')
        return values


class GroupModelBase(BaseModel):
    model_config: ConfigDict = ConfigDict(extra="forbid", from_attributes=True)

    name: constr(max_length=32)
    description: constr(max_length=128)
    admin_id: int
    posts: Optional[List[PostModel]] = []
    subscribers: Optional[List[UserModel]] = []


class GroupModel(GroupModelBase):
    id: int


class GroupModelCreate(GroupModelBase):
    @field_validator("name")
    @classmethod
    def check_unique_name(cls, value):
        if not Group.is_unique_name(value):
            raise ValueError(f'Group name "{value}" is already taken')
        return value


class GroupModelUpdate(GroupModelBase):
    name: Optional[constr(max_length=32)]
    description: Optional[constr(max_length=128)]
    admin_id: Optional[int]


class TokenCreateModel(BaseModel):
    model_config: ConfigDict = ConfigDict(extra="forbid")
    username: constr(max_length=25)
    password: constr(max_length=128)
