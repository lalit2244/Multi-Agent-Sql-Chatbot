"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    """Request model for user queries"""
    question: str = Field(..., description="Natural language question from user", min_length=1)
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=[],
        description="Previous conversation context"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "How many customers do we have?",
                "conversation_history": [
                    {"role": "user", "content": "Show me all products"},
                    {"role": "assistant", "content": "Here are the products..."}
                ]
            }
        }

class QueryResponse(BaseModel):
    """Response model for query results"""
    answer: str = Field(..., description="Natural language answer")
    sql_query: Optional[str] = Field(None, description="Generated SQL query")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="Query results")
    error: Optional[str] = Field(None, description="Error message if any")
    agent_logs: Optional[List[Dict[str, str]]] = Field(
        default=[],
        description="Execution logs from each agent"
    )
    timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Response timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "There are 91 customers in the database.",
                "sql_query": "SELECT COUNT(*) as count FROM Customer",
                "results": [{"count": 91}],
                "error": None,
                "agent_logs": [
                    {"agent": "Schema Analyzer", "status": "Completed"},
                    {"agent": "SQL Generator", "status": "Completed"}
                ],
                "timestamp": "2024-01-04T10:30:00"
            }
        }

class SchemaInfo(BaseModel):
    """Database schema information"""
    tables: List[str] = Field(..., description="List of all table names")
    schema_details: Dict[str, Any] = Field(..., description="Detailed schema information")
    total_tables: Optional[int] = Field(None, description="Total number of tables")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tables": ["Customer", "Order", "Product"],
                "schema_details": {
                    "Customer": {
                        "columns": [
                            {"name": "CustomerID", "type": "INTEGER", "primary_key": True}
                        ]
                    }
                },
                "total_tables": 3
            }
        }

class TableInfo(BaseModel):
    """Information about a single table"""
    table_name: str
    columns: List[Dict[str, Any]]
    foreign_keys: List[Dict[str, Any]]
    sample_data: List[Dict[str, Any]]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    database_connected: bool = Field(..., description="Database connection status")
    total_tables: Optional[int] = Field(None, description="Number of tables in database")
    api_version: Optional[str] = Field(default="1.0.0", description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "All systems operational",
                "database_connected": True,
                "total_tables": 25,
                "api_version": "1.0.0"
            }
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Error timestamp"
    )