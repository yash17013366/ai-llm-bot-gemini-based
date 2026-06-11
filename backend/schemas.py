from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageSchema(BaseModel):
    role: str
    content: str
    created_at: datetime


class ChatSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ChatDetail(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageSchema]


class NewChatResponse(BaseModel):
    chat_id: str
    title: str
    created_at: datetime


class SendMessageRequest(BaseModel):
    chat_id: str = Field(min_length=1)
    content: str = Field(min_length=1)


class SendMessageResponse(BaseModel):
    user_message: MessageSchema
    assistant_message: MessageSchema
    title: str | None = None


class ChatHistoryResponse(BaseModel):
    chats: list[ChatSummary]


class DeleteChatResponse(BaseModel):
    message: str
