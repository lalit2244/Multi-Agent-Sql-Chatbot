"""
Database manager for Northwind Extended database (29 tables)
"""
import sqlite3
import os
from typing import List, Dict, Any, Tuple
import requests
from pathlib import Path

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path: str = "./data/northwind.db"):
        self.db_path = db_path
        self._ensure_database_exists()
        
    def _ensure_database_exists(self):
        """Download Northwind database if not exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(exist_ok=True)
        
        if not os.path.exists(self.db_path):
            print(f"Downloading Northwind database to {self.db_path}...")
            
            urls = [
                "https://raw.githubusercontent.com/jpwhite3/northwind-SQLite3/master/dist/northwind.db",
                "https://github.com/jpwhite3/northwind-SQLite3/raw/master/Northwind_large.sqlite"
            ]
            
            success = False
            for url in urls:
                try:
                    print(f"Trying to download from: {url}")
                    response = requests.get(url, timeout=30)
                    response.raise_for_status()
                    
                    with open(self.db_path, 'wb') as f:
                        f.write(response.content)
                    
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    conn.close()
                    
                    if len(tables) > 0:
                        print(f"✅ Database downloaded successfully! Found {len(tables)} tables.")
                        success = True
                        self._extend_database()
                        break
                    
                except Exception as e:
                    print(f"Failed with this URL: {e}")
                    continue
            
            if not success:
                print("Creating sample database...")
                self._create_sample_database()
    
    def _extend_database(self):
        """Extend database with additional tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        current_count = cursor.fetchone()[0]
        
        print(f"Current table count: {current_count}")
        
        if current_count < 20:
            print("Extending database with additional tables...")
            
            # Warehouse management
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Warehouse (
                    WarehouseID INTEGER PRIMARY KEY,
                    WarehouseName TEXT NOT NULL,
                    Location TEXT,
                    Capacity INTEGER,
                    ManagerID INTEGER
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Inventory (
                    InventoryID INTEGER PRIMARY KEY,
                    ProductID INTEGER,
                    WarehouseID INTEGER,
                    Quantity INTEGER,
                    ReorderLevel INTEGER,
                    LastRestocked DATE
                )
            """)
            
            # Supplier contracts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS SupplierContract (
                    ContractID INTEGER PRIMARY KEY,
                    SupplierID INTEGER,
                    StartDate DATE,
                    EndDate DATE,
                    Terms TEXT,
                    Status TEXT
                )
            """)
            
            # Shipment tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ShipmentTracking (
                    TrackingID INTEGER PRIMARY KEY,
                    OrderID INTEGER,
                    ShipperID INTEGER,
                    TrackingNumber TEXT,
                    ShipDate DATE,
                    EstimatedDelivery DATE,
                    ActualDelivery DATE,
                    Status TEXT
                )
            """)
            
            # Loyalty program
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS LoyaltyProgram (
                    ProgramID INTEGER PRIMARY KEY,
                    ProgramName TEXT,
                    DiscountPercentage REAL,
                    MinimumPurchase REAL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CustomerLoyalty (
                    CustomerID TEXT PRIMARY KEY,
                    ProgramID INTEGER,
                    Points INTEGER,
                    JoinDate DATE,
                    LastPurchaseDate DATE
                )
            """)
            
            # Product reviews
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ProductReview (
                    ReviewID INTEGER PRIMARY KEY,
                    ProductID INTEGER,
                    CustomerID TEXT,
                    Rating INTEGER CHECK(Rating >= 1 AND Rating <= 5),
                    ReviewText TEXT,
                    ReviewDate DATE
                )
            """)
            
            # Marketing campaigns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Campaign (
                    CampaignID INTEGER PRIMARY KEY,
                    CampaignName TEXT,
                    StartDate DATE,
                    EndDate DATE,
                    Budget REAL,
                    TargetAudience TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CampaignProduct (
                    CampaignID INTEGER,
                    ProductID INTEGER,
                    DiscountPercentage REAL,
                    PRIMARY KEY (CampaignID, ProductID)
                )
            """)
            
            # Training programs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS TrainingProgram (
                    ProgramID INTEGER PRIMARY KEY,
                    ProgramName TEXT,
                    Duration INTEGER,
                    Cost REAL,
                    Description TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS EmployeeTraining (
                    EmployeeID INTEGER,
                    ProgramID INTEGER,
                    EnrollmentDate DATE,
                    CompletionDate DATE,
                    Score REAL,
                    PRIMARY KEY (EmployeeID, ProgramID)
                )
            """)
            
            # Sales territories
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS SalesTerritory (
                    TerritoryID INTEGER PRIMARY KEY,
                    TerritoryName TEXT,
                    Region TEXT,
                    Country TEXT,
                    SalesGoal REAL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS EmployeeTerritory (
                    EmployeeID INTEGER,
                    TerritoryID INTEGER,
                    AssignedDate DATE,
                    PRIMARY KEY (EmployeeID, TerritoryID)
                )
            """)
            
            # Returns management
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ProductReturn (
                    ReturnID INTEGER PRIMARY KEY,
                    OrderID INTEGER,
                    ProductID INTEGER,
                    Quantity INTEGER,
                    ReturnDate DATE,
                    Reason TEXT,
                    RefundAmount REAL,
                    Status TEXT
                )
            """)
            
            # Payment methods
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS PaymentMethod (
                    PaymentMethodID INTEGER PRIMARY KEY,
                    CustomerID TEXT,
                    MethodType TEXT,
                    CardLastFour TEXT,
                    ExpiryDate TEXT,
                    IsDefault INTEGER
                )
            """)
            
            conn.commit()
            
            # Insert sample data
            try:
                # Warehouses
                cursor.execute("INSERT OR IGNORE INTO Warehouse VALUES (1, 'Main Warehouse', 'New York, NY', 10000, 1)")
                cursor.execute("INSERT OR IGNORE INTO Warehouse VALUES (2, 'West Coast Hub', 'Los Angeles, CA', 8000, 2)")
                cursor.execute("INSERT OR IGNORE INTO Warehouse VALUES (3, 'East Distribution', 'Boston, MA', 5000, 3)")
                
                # Inventory - Link to actual products
                cursor.execute("""
                    INSERT OR IGNORE INTO Inventory 
                    SELECT 
                        ROW_NUMBER() OVER (ORDER BY ProductID) as InventoryID,
                        ProductID,
                        (ProductID % 3) + 1 as WarehouseID,
                        CAST(RANDOM() % 100 + 50 AS INTEGER) as Quantity,
                        CAST(RANDOM() % 30 + 10 AS INTEGER) as ReorderLevel,
                        date('now', '-' || (RANDOM() % 365) || ' days') as LastRestocked
                    FROM Products
                    LIMIT 50
                """)
                
                # Loyalty Programs
                cursor.execute("INSERT OR IGNORE INTO LoyaltyProgram VALUES (1, 'Gold Member', 10.0, 1000.0)")
                cursor.execute("INSERT OR IGNORE INTO LoyaltyProgram VALUES (2, 'Platinum Member', 15.0, 5000.0)")
                cursor.execute("INSERT OR IGNORE INTO LoyaltyProgram VALUES (3, 'Diamond Member', 20.0, 10000.0)")
                
                # Sales Territories
                cursor.execute("INSERT OR IGNORE INTO SalesTerritory VALUES (1, 'Northeast', 'East', 'USA', 1000000.0)")
                cursor.execute("INSERT OR IGNORE INTO SalesTerritory VALUES (2, 'West', 'West', 'USA', 1200000.0)")
                cursor.execute("INSERT OR IGNORE INTO SalesTerritory VALUES (3, 'Midwest', 'Central', 'USA', 900000.0)")
                
                conn.commit()
            except Exception as e:
                print(f"Sample data insertion error: {e}")
                pass
            
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            new_count = cursor.fetchone()[0]
            print(f"✅ Extended database to {new_count} tables!")
        
        conn.close()
    
    def _create_sample_database(self):
        """Create sample database if download fails"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE Customer (
                CustomerID TEXT PRIMARY KEY,
                CompanyName TEXT,
                ContactName TEXT,
                Country TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE Product (
                ProductID INTEGER PRIMARY KEY,
                ProductName TEXT,
                UnitPrice REAL
            )
        """)
        
        conn.commit()
        self._extend_database()
        conn.close()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get complete database schema information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        schema_info = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info([{table}])")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'name': row[1],
                    'type': row[2],
                    'notnull': bool(row[3]),
                    'default_value': row[4],
                    'primary_key': bool(row[5])
                })
            
            cursor.execute(f"PRAGMA foreign_key_list([{table}])")
            foreign_keys = []
            for row in cursor.fetchall():
                foreign_keys.append({
                    'column': row[3],
                    'references_table': row[2],
                    'references_column': row[4]
                })
            
            # Get sample data with binary handling
            try:
                cursor.execute(f"SELECT * FROM [{table}] LIMIT 2")
                rows = cursor.fetchall()
                sample_data = []
                for row in rows:
                    row_dict = {}
                    for key in row.keys():
                        value = row[key]
                        if isinstance(value, bytes):
                            row_dict[key] = f"<binary data: {len(value)} bytes>"
                        else:
                            row_dict[key] = value
                    sample_data.append(row_dict)
            except:
                sample_data = []
            
            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
                row_count = cursor.fetchone()[0]
            except:
                row_count = 0
            
            schema_info[table] = {
                'columns': columns,
                'foreign_keys': foreign_keys,
                'sample_data': sample_data,
                'row_count': row_count
            }
        
        conn.close()
        return schema_info
    
    def execute_query(self, sql: str) -> Tuple[List[Dict[str, Any]], str]:
        """Execute SQL query and return results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            sql_upper = sql.strip().upper()
            if not sql_upper.startswith('SELECT') and not sql_upper.startswith('WITH'):
                return [], "Only SELECT queries are allowed for security reasons"
            
            dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    return [], f"Query contains forbidden keyword: {keyword}"
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            # Handle binary data in results
            results = []
            for row in rows:
                row_dict = {}
                for key in row.keys():
                    value = row[key]
                    if isinstance(value, bytes):
                        row_dict[key] = f"<binary data: {len(value)} bytes>"
                    else:
                        row_dict[key] = value
                results.append(row_dict)
            
            conn.close()
            return results, None
            
        except Exception as e:
            return [], str(e)
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except:
            return False
    
    def get_table_names(self) -> List[str]:
        """Get list of all table names"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    
    def get_table_count(self) -> int:
        """Get total number of tables"""
        return len(self.get_table_names())