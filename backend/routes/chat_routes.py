from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, status

from auth import get_current_user_id
from database import get_database
from schemas import (
    ChatDetail,
    ChatHistoryResponse,
    ChatSummary,
    DeleteChatResponse,
    MessageSchema,
    NewChatResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from services.ai_service import generate_response

router = APIRouter(prefix="/chat", tags=["chat"])

DEFAULT_CHAT_TITLE = "New Chat"
MAX_TITLE_LENGTH = 50


def _validate_object_id(value: str, field_name: str = "id") -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format",
        )
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format",
        )


def _get_owned_chat(chat_id: str, user_id: str):
    db = get_database()
    chat_object_id = _validate_object_id(chat_id, "chat_id")
    user_object_id = ObjectId(user_id)

    chat = db.chats.find_one({"_id": chat_object_id})
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    if chat["user_id"] != user_object_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return chat, chat_object_id


def _generate_title(content: str) -> str:
    cleaned = " ".join(content.strip().split())
    if not cleaned:
        return DEFAULT_CHAT_TITLE
    if len(cleaned) <= MAX_TITLE_LENGTH:
        return cleaned
    return f"{cleaned[:MAX_TITLE_LENGTH].rstrip()}..."


def _serialize_message(message: dict) -> MessageSchema:
    return MessageSchema(
        role=message["role"],
        content=message["content"],
        created_at=message["created_at"],
    )


@router.post("/new", response_model=NewChatResponse)
def create_chat(user_id: str = Depends(get_current_user_id)) -> NewChatResponse:
    db = get_database()
    now = datetime.now(timezone.utc)

    chat_document = {
        "user_id": ObjectId(user_id),
        "title": DEFAULT_CHAT_TITLE,
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }

    result = db.chats.insert_one(chat_document)

    return NewChatResponse(
        chat_id=str(result.inserted_id),
        title=DEFAULT_CHAT_TITLE,
        created_at=now,
    )


@router.post("/message", response_model=SendMessageResponse)
def send_message(
    payload: SendMessageRequest,
    user_id: str = Depends(get_current_user_id),
) -> SendMessageResponse:
    db = get_database()
    chat, chat_object_id = _get_owned_chat(payload.chat_id, user_id)
    now = datetime.now(timezone.utc)

    user_message = {
        "role": "user",
        "content": payload.content.strip(),
        "created_at": now,
    }

    existing_messages = chat.get("messages", [])
    is_first_message = len(existing_messages) == 0
    updated_title = chat["title"]

    if is_first_message:
        updated_title = _generate_title(payload.content)

    context_messages = existing_messages + [user_message]
    ai_content = generate_response(
        [{"role": m["role"], "content": m["content"]} for m in context_messages]
    )

    assistant_message = {
        "role": "assistant",
        "content": ai_content,
        "created_at": datetime.now(timezone.utc),
    }

    update_fields = {
        "$push": {"messages": {"$each": [user_message, assistant_message]}},
        "$set": {"updated_at": datetime.now(timezone.utc)},
    }

    if is_first_message:
        update_fields["$set"]["title"] = updated_title

    db.chats.update_one({"_id": chat_object_id}, update_fields)

    response = SendMessageResponse(
        user_message=_serialize_message(user_message),
        assistant_message=_serialize_message(assistant_message),
    )

    if is_first_message:
        response.title = updated_title

    return response


@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history(user_id: str = Depends(get_current_user_id)) -> ChatHistoryResponse:
    db = get_database()
    chats_cursor = db.chats.find({"user_id": ObjectId(user_id)}).sort("updated_at", -1)

    chats = [
        ChatSummary(
            id=str(chat["_id"]),
            title=chat.get("title", DEFAULT_CHAT_TITLE),
            created_at=chat["created_at"],
            updated_at=chat["updated_at"],
        )
        for chat in chats_cursor
    ]

    return ChatHistoryResponse(chats=chats)


@router.get("/{chat_id}", response_model=ChatDetail)
def get_chat(chat_id: str, user_id: str = Depends(get_current_user_id)) -> ChatDetail:
    chat, _ = _get_owned_chat(chat_id, user_id)

    return ChatDetail(
        id=str(chat["_id"]),
        title=chat.get("title", DEFAULT_CHAT_TITLE),
        created_at=chat["created_at"],
        updated_at=chat["updated_at"],
        messages=[_serialize_message(message) for message in chat.get("messages", [])],
    )


@router.delete("/{chat_id}", response_model=DeleteChatResponse)
def delete_chat(chat_id: str, user_id: str = Depends(get_current_user_id)) -> DeleteChatResponse:
    db = get_database()
    _, chat_object_id = _get_owned_chat(chat_id, user_id)

    db.chats.delete_one({"_id": chat_object_id})

    return DeleteChatResponse(message="Chat deleted successfully")
