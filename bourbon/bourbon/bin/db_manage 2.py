import sqlalchemy 
from importlib import resources 
from bourbon.log_fx import setup_log

with resources.path("bourbon.logs","db_manage.log") as f: 
    logger = setup_log(f, 'db_manager')

with resources.path("bourbon","buffalo_trace.db") as db_path: 
    if not db_path.exists(): 
        raise FileNotFoundError("DB File not found")
    

    sql_url = f"sqlite:////{db_path.absolute()}"

    # test connection 
    engine = sqlalchemy.create_engine(sql_url)

with engine.connect() as my_conn: 
    with my_conn.begin(): 
        version = my_conn.execute(sqlalchemy.text("select sqlite_version()")).fetchone()[0]

        logger.debug(f"connected to sql at version {version}")

# get tables 
inspector = sqlalchemy.inspect(engine)
my_tables = inspector.get_table_names()
logger.info(f"Tables Present = {my_tables}")

    