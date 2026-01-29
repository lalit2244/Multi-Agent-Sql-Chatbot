import os
import json
from typing import Dict, Any, List, Tuple
from groq import Groq
from .database import DatabaseManager

class MultiAgentSystem:
    """
    Multi-agent system for Text-to-SQL conversion
    Agents:
    1. Schema Analyzer - Analyzes DB schema and finds relevant tables
    2. SQL Generator - Converts natural language to SQL
    3. Query Executor - Executes SQL and handles errors
    4. Response Formatter - Formats results into natural language
    """
    
    def __init__(self, groq_api_key: str, db_manager: DatabaseManager):
        self.client = Groq(api_key=groq_api_key)
        self.db_manager = db_manager
        self.model = "llama-3.3-70b-versatile"
        self.agent_logs = []
        
    def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
        """Call Groq LLM with prompts"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=3000  # Increased for longer queries
            )
            result = response.choices[0].message.content
            print(f"[LLM Response] {result[:200]}...")
            return result
        except Exception as e:
            error_msg = f"Error calling LLM: {str(e)}"
            print(f"[LLM Error] {error_msg}")
            return error_msg
    
    def agent_1_schema_analyzer(self, question: str) -> Dict[str, Any]:
        """Agent 1: Analyze schema and identify relevant tables"""
        self.agent_logs.append({"agent": "Schema Analyzer", "status": "Starting..."})
        
        schema_info = self.db_manager.get_schema_info()
        tables = list(schema_info.keys())
        
        schema_summary = "Database Schema:\n\n"
        for table, info in schema_info.items():
            schema_summary += f"\nTable: {table}\n"
            schema_summary += "Columns:\n"
            for col in info['columns']:
                pk = " (PRIMARY KEY)" if col['primary_key'] else ""
                schema_summary += f"  - {col['name']}: {col['type']}{pk}\n"
            if info['foreign_keys']:
                schema_summary += "Foreign Keys:\n"
                for fk in info['foreign_keys']:
                    schema_summary += f"  - {fk['column']} -> {fk['references_table']}.{fk['references_column']}\n"
        
        system_prompt = """You are a database schema expert. Given a user question and database schema, 
        identify which tables are relevant to answer the question. 
        Return ONLY a JSON object with: {"relevant_tables": ["table1", "table2"], "reasoning": "brief explanation"}"""
        
        user_prompt = f"Question: {question}\n\n{schema_summary}\n\nIdentify relevant tables:"
        
        response = self._call_llm(system_prompt, user_prompt)
        
        try:
            result = json.loads(response)
            relevant_tables = result.get('relevant_tables', tables)
            reasoning = result.get('reasoning', 'All tables considered')
        except:
            relevant_tables = tables
            reasoning = "Using all tables due to parsing error"
        
        relevant_schema = {table: schema_info[table] for table in relevant_tables if table in schema_info}
        
        self.agent_logs.append({
            "agent": "Schema Analyzer",
            "status": "Completed",
            "output": f"Identified {len(relevant_tables)} relevant tables: {', '.join(relevant_tables)}"
        })
        
        return {
            "relevant_tables": relevant_tables,
            "relevant_schema": relevant_schema,
            "reasoning": reasoning,
            "full_schema": schema_info
        }
    
    def agent_2_sql_generator(self, question: str, schema_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Agent 2: Generate SQL query from natural language"""
        self.agent_logs.append({"agent": "SQL Generator", "status": "Starting..."})
        
        relevant_schema = schema_analysis['relevant_schema']
        
        schema_text = "Available Tables:\n"
        for table, info in relevant_schema.items():
            schema_text += f"\nTable: {table}\nColumns: "
            columns = [col['name'] for col in info['columns']]
            schema_text += ", ".join(columns) + "\n"
        
        system_prompt = """You are a SQL expert. Generate a COMPLETE and EFFICIENT SQLite SELECT query.

CRITICAL RULES:
1. Return the COMPLETE query on a SINGLE LINE
2. Use ONLY the tables needed to answer the question
3. Keep queries as simple as possible
4. Return ONLY the SQL query - no explanations, no markdown
5. Ensure the query is complete - no truncation

Examples:
- "Total revenue" → SELECT SUM(UnitPrice * Quantity) FROM [Order Details]
- "Customers who never ordered" → SELECT * FROM Customers WHERE CustomerID NOT IN (SELECT DISTINCT CustomerID FROM Orders)
- "Products by category" → SELECT p.ProductName, c.CategoryName FROM Products p JOIN Categories c ON p.CategoryID = c.CategoryID"""
        
        user_prompt = f"""Question: {question}

{schema_text}

Write a SELECT query:"""
        
        sql_response = self._call_llm(system_prompt, user_prompt, temperature=0.0)
        
        sql_query = sql_response.strip()
        sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        
        if 'SELECT' in sql_query.upper():
            select_index = sql_query.upper().index('SELECT')
            sql_query = sql_query[select_index:].strip()
        
        if ';' in sql_query:
            sql_query = sql_query.split(';')[0].strip()
        
        if not sql_query or 'SELECT' not in sql_query.upper() or len(sql_query) < 10:
            question_lower = question.lower()
            
            if 'never' in question_lower and ('order' in question_lower or 'placed' in question_lower):
                # Customers who never ordered
                sql_query = "SELECT * FROM Customers WHERE CustomerID NOT IN (SELECT DISTINCT CustomerID FROM Orders)"
            elif 'never' in question_lower and 'ordered' in question_lower and 'product' in question_lower:
                # Products never ordered
                sql_query = "SELECT * FROM Products WHERE ProductID NOT IN (SELECT DISTINCT ProductID FROM [Order Details])"
            elif 'revenue' in question_lower or 'sales' in question_lower or 'total' in question_lower:
                sql_query = "SELECT SUM(UnitPrice * Quantity * (1 - Discount)) AS TotalRevenue FROM [Order Details]"
            elif 'inventory' in question_lower or 'stock' in question_lower:
                sql_query = """SELECT p.ProductName, i.Quantity, i.ReorderLevel, w.WarehouseName 
                FROM Inventory i 
                JOIN Products p ON i.ProductID = p.ProductID 
                JOIN Warehouse w ON i.WarehouseID = w.WarehouseID 
                LIMIT 20"""
            elif 'product' in question_lower:
                sql_query = "SELECT * FROM Products LIMIT 10"
            elif 'customer' in question_lower:
                sql_query = "SELECT * FROM Customers LIMIT 10"
            elif 'order' in question_lower:
                sql_query = "SELECT * FROM Orders LIMIT 10"
            elif 'employee' in question_lower:
                sql_query = "SELECT * FROM Employees LIMIT 10"
            elif 'count' in question_lower or 'how many' in question_lower:
                if relevant_schema:
                    first_table = list(relevant_schema.keys())[0]
                    sql_query = f"SELECT COUNT(*) as total FROM [{first_table}]"
                else:
                    sql_query = "SELECT COUNT(*) as total FROM Products"
            else:
                if relevant_schema:
                    first_table = list(relevant_schema.keys())[0]
                    sql_query = f"SELECT * FROM [{first_table}] LIMIT 10"
                else:
                    sql_query = "SELECT * FROM Products LIMIT 10"
        
        self.agent_logs.append({
            "agent": "SQL Generator",
            "status": "Completed",
            "output": f"Generated SQL query: {sql_query[:100]}..."
        })
        
        return {
            "sql_query": sql_query,
            "schema_context": schema_text
        }
    
    def agent_3_query_executor(self, sql_query: str) -> Dict[str, Any]:
        """Agent 3: Execute SQL query safely"""
        self.agent_logs.append({"agent": "Query Executor", "status": "Starting..."})
        
        results, error = self.db_manager.execute_query(sql_query)
        
        if error:
            self.agent_logs.append({
                "agent": "Query Executor",
                "status": "Error",
                "output": f"Query execution failed: {error}"
            })
            return {
                "success": False,
                "results": [],
                "error": error
            }
        
        self.agent_logs.append({
            "agent": "Query Executor",
            "status": "Completed",
            "output": f"Query executed successfully. Returned {len(results)} rows."
        })
        
        return {
            "success": True,
            "results": results,
            "error": None
        }
    
    def agent_4_response_formatter(self, question: str, sql_query: str, 
                                   execution_result: Dict[str, Any]) -> str:
        """Agent 4: Format results into natural language response"""
        self.agent_logs.append({"agent": "Response Formatter", "status": "Starting..."})
        
        if not execution_result['success']:
            response = f"I encountered an error while trying to answer your question: {execution_result['error']}"
            self.agent_logs.append({
                "agent": "Response Formatter",
                "status": "Completed (Error Response)",
                "output": response
            })
            return response
        
        results = execution_result['results']
        
        if not results:
            if 'inventory' in sql_query.lower() or 'stock' in sql_query.lower():
                response = """The inventory query executed successfully, but no data was found. 
                
This could mean:
- The Inventory table might be empty or not linked to products yet
- Try asking: "How many products do we have?" or "Show me all products"
- The database may need inventory data to be populated

Would you like to try a different query?"""
            elif 'WHERE' in sql_query.upper():
                response = """The query executed successfully, but no records matched your criteria.

Try:
- Removing some filters
- Using broader search terms
- Checking if the data exists with a simpler query"""
            else:
                response = "The query executed successfully but returned no data. The table might be empty or the data doesn't exist yet."
            
            self.agent_logs.append({
                "agent": "Response Formatter",
                "status": "Completed (No Results)",
                "output": response
            })
            return response
        
        results_text = f"Query returned {len(results)} rows.\n\n"
        if len(results) <= 10:
            results_text += "Full Results:\n" + json.dumps(results, indent=2, default=str)
        else:
            results_text += "First 10 Results:\n" + json.dumps(results[:10], indent=2, default=str)
        
        system_prompt = """You are a helpful data analyst. Convert SQL query results into a clear, 
        natural language response. Be concise but informative. If there are many results, 
        summarize them intelligently. Include key insights. Always be positive and helpful."""
        
        user_prompt = f"""Original Question: {question}

SQL Query Used: {sql_query}

{results_text}

Provide a natural language answer:"""
        
        natural_response = self._call_llm(system_prompt, user_prompt, temperature=0.3)
        
        self.agent_logs.append({
            "agent": "Response Formatter",
            "status": "Completed",
            "output": "Generated natural language response"
        })
        
        return natural_response
    
    def process_query(self, question: str) -> Dict[str, Any]:
        """Main orchestration method - runs all agents in sequence"""
        self.agent_logs = []
        
        try:
            schema_analysis = self.agent_1_schema_analyzer(question)
            sql_generation = self.agent_2_sql_generator(question, schema_analysis)
            sql_query = sql_generation['sql_query']
            execution_result = self.agent_3_query_executor(sql_query)
            natural_response = self.agent_4_response_formatter(
                question, sql_query, execution_result
            )
            
            return {
                "answer": natural_response,
                "sql_query": sql_query,
                "results": execution_result['results'],
                "error": execution_result.get('error'),
                "agent_logs": self.agent_logs,
                "success": execution_result['success']
            }
            
        except Exception as e:
            error_msg = f"System error: {str(e)}"
            self.agent_logs.append({
                "agent": "System",
                "status": "Error",
                "output": error_msg
            })
            return {
                "answer": f"I apologize, but I encountered an error: {str(e)}",
                "sql_query": None,
                "results": [],
                "error": str(e),
                "agent_logs": self.agent_logs,
                "success": False
            }