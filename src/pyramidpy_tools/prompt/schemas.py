# https://github.com/TavernAI/
from typing import List, Optional

from pydantic import BaseModel


class CharacterMetadata(BaseModel):
    alternate_greetings: List[any] = []
    avatar: Optional[str] = None
    character_book: Optional[str] = None
    character_version: Optional[str] = None
    char_persona: Optional[str] = None
    char_name: Optional[str] = None
    chat: Optional[str] = None
    create_date: Optional[str] = None
    creator: Optional[str] = None
    creator_notes: Optional[str] = None
    description: Optional[str] = None
    first_message: Optional[str] = None
    message_example: Optional[str] = None
    name: Optional[str] = None
    personality: Optional[str] = None
    post_history_instructions: Optional[str] = None
    scenario: Optional[str] = None
    system_prompt: Optional[str] = None
    tags: List[str] = []
    char_greeting: Optional[str] = None
    world_scenario: Optional[str] = None
    example_dialogues: List[str] = []


class Character(BaseModel):
    """
    Schema for a character.
    Compatible with the persona_prompt_v1.
    """

    metadata: CharacterMetadata
    fallback_avatar: str = ""

    @property
    def avatar(self) -> str:
        if self.metadata.avatar and self.metadata.avatar != "none":
            return self.metadata.avatar
        return self.fallback_avatar

    @property
    def description(self) -> str:
        return self.metadata.system_prompt or self.metadata.description or ""

    @property
    def name(self) -> str:
        return self.metadata.name or self.metadata.char_name or ""

    @property
    def char_persona(self) -> str:
        return self.metadata.char_persona or ""
