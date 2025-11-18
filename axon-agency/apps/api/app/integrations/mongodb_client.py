"""MongoDB client for WhatsApp Sales Agent persistence.

Provides async CRUD operations for:
- users: WhatsApp user profiles
- messages: Message history (in/out)
- leads: Qualified leads data
- sessions: Conversation state tracking
"""

from datetime import datetime
from typing import Optional, List, Literal, Any, cast
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from loguru import logger
from pymongo import ReturnDocument


class User(BaseModel):
    """WhatsApp user profile."""
    phone: str
    name: Optional[str] = None
    sector: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_seen_at: datetime = Field(default_factory=datetime.utcnow)


class Message(BaseModel):
    """WhatsApp message (incoming or outgoing)."""
    phone: str
    direction: Literal["in", "out"]
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    intent: Optional[str] = None


class Lead(BaseModel):
    """Qualified lead data with LinkedIn enrichment."""
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    empresa: Optional[str] = None
    sector: Optional[str] = None
    tamano_empresa: Optional[str] = None
    presupuesto_aprox: Optional[str] = None
    
    linkedin_role: Optional[str] = None
    linkedin_company_size: Optional[str] = None
    linkedin_location: Optional[str] = None
    linkedin_industry: Optional[str] = None
    
    estado: str = "nuevo"
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Session(BaseModel):
    """Conversation state tracking."""
    phone: str
    current_step: str = "greet"
    answers: dict = Field(default_factory=dict)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)


class MongoDBClient:
    """Async MongoDB client for WhatsApp Sales Agent."""
    
    def __init__(self, uri: str, db_name: str):
        """Initialize MongoDB client.
        
        Args:
            uri: MongoDB connection URI
            db_name: Database name
        """
        self.uri = uri
        self.uri_truncated = uri[:20] + "..." if len(uri) > 20 else uri
        self.db_name = db_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Any = None
    
    async def connect(self):
        """Connect to MongoDB. Call once at startup."""
        try:
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client[self.db_name]
            await self.client.admin.command('ping')
            logger.info(f"MongoDB connected successfully. Database: {self.db_name}")
        except Exception as e:
            error_msg = str(e)[:200]
            logger.error(f"MongoDB connection failed: {error_msg}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB. Call at shutdown."""
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")
    
    async def upsert_user(self, phone: str, name: Optional[str] = None, sector: Optional[str] = None) -> User:
        """Create or update user. Updates last_seen_at on every call.
        
        Args:
            phone: WhatsApp phone number
            name: User name (optional)
            sector: User sector/industry (optional)
            
        Returns:
            User: Updated or created user
        """
        now = datetime.utcnow()
        update_data: dict[str, Any] = {"last_seen_at": now}
        if name:
            update_data["name"] = name
        if sector:
            update_data["sector"] = sector
        
        result = await self.db.users.find_one_and_update(
            {"phone": phone},
            {
                "$set": update_data,
                "$setOnInsert": {"created_at": now}
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return User(**result)
    
    async def get_user(self, phone: str) -> Optional[User]:
        """Get user by phone number.
        
        Args:
            phone: WhatsApp phone number
            
        Returns:
            User or None if not found
        """
        result = await self.db.users.find_one({"phone": phone})
        return User(**result) if result else None
    
    async def insert_message(self, phone: str, direction: Literal["in", "out"], text: str, intent: Optional[str] = None) -> Message:
        """Insert new message (incoming or outgoing).
        
        Args:
            phone: WhatsApp phone number
            direction: "in" or "out"
            text: Message text
            intent: Optional OpenAI classified intent
            
        Returns:
            Message: Created message
        """
        message = Message(phone=phone, direction=direction, text=text, intent=intent)
        await self.db.messages.insert_one(message.model_dump())
        phone_truncated = phone[:10] + "..." if len(phone) > 10 else phone
        logger.info(f"Message saved: {direction} from {phone_truncated}")
        return message
    
    async def get_recent_messages(self, phone: str, limit: int = 10) -> List[Message]:
        """Get recent messages for conversation history.
        
        Args:
            phone: WhatsApp phone number
            limit: Maximum number of messages to return
            
        Returns:
            List of messages (oldest first)
        """
        cursor = self.db.messages.find({"phone": phone}).sort("timestamp", -1).limit(limit)
        messages = await cursor.to_list(length=limit)
        return [Message(**msg) for msg in reversed(messages)]
    
    async def upsert_lead(self, phone: str, **lead_data) -> Lead:
        """Create or update lead with provided data.
        
        Args:
            phone: WhatsApp phone number
            **lead_data: Lead fields to update
            
        Returns:
            Lead: Updated or created lead
        """
        now = datetime.utcnow()
        lead_data["phone"] = phone
        lead_data["updated_at"] = now
        
        result = await self.db.leads.find_one_and_update(
            {"phone": phone},
            {
                "$set": lead_data,
                "$setOnInsert": {"created_at": now, "estado": "nuevo"}
            },
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        phone_truncated = phone[:10] + "..." if len(phone) > 10 else phone
        logger.info(f"Lead upserted: {phone_truncated} estado={result.get('estado')}")
        return Lead(**result)
    
    async def get_lead(self, phone: str) -> Optional[Lead]:
        """Get lead by phone number.
        
        Args:
            phone: WhatsApp phone number
            
        Returns:
            Lead or None if not found
        """
        result = await self.db.leads.find_one({"phone": phone})
        return Lead(**result) if result else None
    
    async def load_or_create_session(self, phone: str) -> Session:
        """Load existing session or create new one.
        
        Args:
            phone: WhatsApp phone number
            
        Returns:
            Session: Existing or new session
        """
        result = await self.db.sessions.find_one({"phone": phone})
        if result:
            return Session(**result)
        
        session = Session(phone=phone)
        await self.db.sessions.insert_one(session.model_dump())
        phone_truncated = phone[:10] + "..." if len(phone) > 10 else phone
        logger.info(f"New session created for {phone_truncated}")
        return session
    
    async def update_session(self, phone: str, current_step: str, answers: dict) -> Session:
        """Update session step and answers.
        
        Args:
            phone: WhatsApp phone number
            current_step: Current conversation step
            answers: User answers collected
            
        Returns:
            Session: Updated session
        """
        now = datetime.utcnow()
        result = await self.db.sessions.find_one_and_update(
            {"phone": phone},
            {
                "$set": {
                    "current_step": current_step,
                    "answers": answers,
                    "last_updated_at": now
                }
            },
            return_document=ReturnDocument.AFTER
        )
        return Session(**result)
