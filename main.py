from twisted.internet import task, reactor
import mysqldb
import os

timeout = 60.0

geoDB = mysqldb.Database(
  os.environ.get("MYSQL_HOSTNAME"),
  os.environ.get("MYSQL_GT_USER"),
  os.environ.get("MYSQL_GT_PASSWORD"),
  os.environ.get("GT_GEO_DATABASE")
)
baseDB = mysqldb.Database(
  host=os.environ.get("MYSQL_HOSTNAME"),
  user=os.environ.get("MYSQL_GT_USER"),
  password=os.environ.get("MYSQL_GT_PASSWORD"),
  database=os.environ.get("GT_BASE_DATABASE")
)
baseTable=os.environ.get("GT_BASE_TABLE")
baseColumn=os.environ.get("GT_BASE_IP_COLUMN")

def fixSchema():
  alterQuery = """
      ALTER TABLE %s
      ADD (latitude float, longitude float, postal_code text)
  """  %(baseTable)
  result = baseDB.query(alterQuery)
  result.fetchall()

def main():
  ignoreAddresses = os.environ.get("GT_IGNORE_IPS").split(",")

  # Verify schema is correct
  if not baseDB.query(f"SHOW COLUMNS from %s LIKE 'latitude'" %(baseTable)).fetchall():
    fixSchema()

  for session in baseDB.fetch(f"SELECT id, %s FROM %s WHERE longitude IS NULL" %(baseColumn, baseTable)):
    if session[1] not in ignoreAddresses:
      locationQuery = f"""
          SELECT latitude, longitude, postal_code
          FROM geoip2_network
          WHERE inet6_aton("%s") between network_start and network_end
          limit 1;
      """ %(session[1])
      result=geoDB.query(locationQuery).fetchall()
      if result:
        updateQuery = f"""
            UPDATE %s
            SET latitude=%f, longitude=%f, postal_code="%s"
            WHERE id="%s"
        """ %(baseTable, result[0][0], result[0][1], result[0][2], session[0])
        updateResult = baseDB.update(updateQuery)

        if updateResult:
          print("Session ID: %s, successfully updated location data." %(session[0]))
      else:
        print("[WARN] Unable to tag %s (%s)." %(session[0], session[1]))

loop = task.LoopingCall(main)
loop.start(timeout)
reactor.run()
