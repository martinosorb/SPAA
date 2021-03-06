import sqlite3
import datajuicer.in_out as in_out

def _format_value(val):
    if type(val) == int:
        return str(val)
    if type(val) == float:
        return str(val)
    return "\"" + str(val) + "\""

def _format_key(key):
    return f"\"{key}\""
def select(db_file, column, table, where, order_by):
    table = '\"' + table + '\"'
    try:
        conn = sqlite3.connect(db_file)
        command = f"SELECT {column} FROM {table} WHERE "
        command += " AND ".join([f"{_format_key(key)}={_format_value(value)}" for key, value in where.items()])
        command += f" ORDER BY {order_by} DESC;"
        cur = conn.cursor()
        cur.execute(command)
        result = [sid[0] for sid in cur.fetchall()] 
    except sqlite3.Error as error:
        return []
    
    if (conn):
        conn.close()
    
    return result

def insert(db_file, table, row, primary_key):
    table = '\"' + table + '\"'
    try:
        row.pop('')
    except:
        pass
    fieldset = []
    for key, val in row.items():
        if type(val) == int:
            definition = "INTEGER"
        elif type(val) == float:
            definition = "REAL"
        else:
            definition = "TEXT"
        if key == primary_key:
            fieldset.append(f"{_format_key(key)} {definition} PRIMARY KEY")
        else:
            fieldset.append(f"{_format_key(key)} {definition}")

    create_table = "CREATE TABLE IF NOT EXISTS {0} ({1});".format(table, ", ".join(fieldset))

    insert = f"INSERT INTO {table} ("
    insert += ", ".join([_format_key(key) for key in row])
    insert += ") VALUES("
    insert += ", ".join([_format_value(value) for value in row.values()])
    insert += ");"

    in_out.make_dir(db_file)
    try:
        conn = sqlite3.connect(db_file, timeout=100)
        c = conn.cursor()
        c.execute(create_table)
        c.execute(insert)
        conn.commit()
        c.close()
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
        raise Exception
    finally:
        if (conn):
            conn.close()
