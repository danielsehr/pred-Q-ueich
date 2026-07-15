from sqlalchemy import inspect, text, Engine

from discharge_queich.database.db import engine


def inspect_table(
    table_name: str,
    engine: Engine = engine, 
    ) -> None:
    
    inspector = inspect(engine)

    print(f"\n=== {table_name} ===")

    print("\nColumns:")
    for col in inspector.get_columns(table_name):
        print(f"  {col['name']}: {col['type']}")

    print("\nUnique constraints:")
    for uc in inspector.get_unique_constraints(table_name):
        print(f"  {uc}")

    print("\nIndexes:")
    for idx in inspector.get_indexes(table_name):
        print(f"  {idx}")
        
    print("\nPrimary key:")
    print(inspector.get_pk_constraint(table_name))

    print("\nForeign keys:")
    for fk in inspector.get_foreign_keys(table_name):
        print(f"  {fk}")

    with engine.connect() as conn:
        schema = conn.execute(
            text(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name=:name"
            ),
            {"name": table_name},
        ).scalar_one()

    print("\nCREATE TABLE:")
    print(schema)