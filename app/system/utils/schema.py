"""module to formate made reuests to workflow"""
from pydantic import BaseModel


# we need consistent formatting for made requests and agent response
class UserRequest(BaseModel):
    """Blueprint for user requests (request body should provide `text`)."""
    text: str


class AgentResponse(BaseModel):
    """blueprint for agent response"""
    response: str
