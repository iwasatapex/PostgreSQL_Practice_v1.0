"""
database/schema_reader.py

Reads PostgreSQL schema and builds a complete model.
"""

from database.postgres import PostgreSQL
from models.table import Table
from models.column import Column
from models.relationship import Relationship


class SchemaReader:
    """Reads PostgreSQL database schema."""

    def __init__(self):
        self.db = PostgreSQL()

    def read_schema(self):
        """Read complete schema and return Table objects."""
        
        self.db.connect()

        # 1. Get all tables in public schema
        tables = self._read_tables()

        # 2. Get columns for each table
        self._read_columns(tables)

        # 3. Get primary keys
        self._read_primary_keys(tables)

        # 4. Get foreign keys
        self._read_foreign_keys(tables)

        self.db.disconnect()
        return tables

    def _read_tables(self):
        """Read all table names from public schema."""
        
        rows = self.db.fetchall("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = []
        for row in rows:
            tables.append(Table(name=row[0]))

        return tables

    def _read_columns(self, tables):
        """Read columns for each table."""
        
        for table in tables:
            rows = self.db.fetchall("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                ORDER BY ordinal_position;
            """, (table.name,))

            for row in rows:
                column = Column(
                    name=row[0],
                    data_type=row[1],
                    nullable=(row[2] == 'YES'),
                    default=row[3]
                )
                table.columns.append(column)

    def _read_primary_keys(self, tables):
        """Read primary keys and mark columns."""
        
        # Create a lookup dict for faster access
        table_dict = {t.name: t for t in tables}

        rows = self.db.fetchall("""
            SELECT
                tc.table_name,
                kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema = 'public';
        """)

        for table_name, column_name in rows:
            table = table_dict.get(table_name)
            if table is None:
                continue
            
            for column in table.columns:
                if column.name == column_name:
                    column.primary_key = True

    def _read_foreign_keys(self, tables):
        """Read foreign keys and mark columns."""
        
        # Create a lookup dict for faster access
        table_dict = {t.name: t for t in tables}

        rows = self.db.fetchall("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS target_table,
                ccu.column_name AS target_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
                AND tc.table_schema = ccu.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public';
        """)

        for source_table, source_col, target_table, target_col in rows:
            table = table_dict.get(source_table)
            if table is None:
                continue

            # Mark the column as foreign key
            for column in table.columns:
                if column.name == source_col:
                    column.foreign_key = True

            # Store the relationship
            table.relationships.append(
                Relationship(
                    source_column=source_col,
                    target_table=target_table,
                    target_column=target_col
                )
            )
