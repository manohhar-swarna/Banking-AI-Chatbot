from pydantic import BaseModel, Field


# -------------------- Pydantic Schemas -------------------- #
#which is used as custom defined data types.

class FindEmployeeInformation(BaseModel):
    """Input for the finding employee information queries"""
    name: str = Field(description="name of the employee")


class FindEmployeeEmail(BaseModel):
    """Input for finding employee email id """
    name: str = Field(description="name of the employee")


class FindEmployeeId(BaseModel):
    """Input for the finding employee id queries"""
    name: str = Field(description="name of the employee")


class SearchQuery(BaseModel):
    """Input for search query"""
    user_query: str = Field(description="what is the user query to search for")


class FindUserInformation(BaseModel):
    """Input for finding user information queries"""
    name: str = Field(description="name of the user")