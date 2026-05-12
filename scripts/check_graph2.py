import boto3, json

session = boto3.Session(profile_name="gapv50k", region_name="ap-southeast-1")
neptune = session.client("neptune-graph")
graph_id = "g-0keuwoev4a"

def query(q):
    resp = neptune.execute_query(graphIdentifier=graph_id, queryString=q, language="OPEN_CYPHER")
    return json.loads(resp["payload"].read()).get("results", [])

# What do Entity nodes look like?
print("=== Sample Entity nodes (first 30) ===")
for row in query("MATCH (n:Entity) RETURN n.value AS entity LIMIT 30"):
    print(f"  {row.get('entity','?')}")

print("\n=== Entity properties ===")
for row in query("MATCH (n:Entity) RETURN keys(n) AS props LIMIT 1"):
    print(f"  {row}")

print("\n=== Entities containing drug names ===")
for row in query("MATCH (n:Entity) WHERE toLower(n.value) CONTAINS 'dexamethasone' OR toLower(n.value) CONTAINS 'tocilizumab' OR toLower(n.value) CONTAINS 'remdesivir' OR toLower(n.value) CONTAINS 'nirmatrelvir' OR toLower(n.value) CONTAINS 'heparin' OR toLower(n.value) CONTAINS 'baricitinib' OR toLower(n.value) CONTAINS 'molnupiravir' RETURN n.value AS entity LIMIT 30"):
    print(f"  {row.get('entity','?')}")

print("\n=== How entities connect to chunks ===")
for row in query("MATCH (e:Entity)-[r:CONTAINS]-(c:Chunk) WHERE toLower(e.value) CONTAINS 'nirmatrelvir' RETURN e.value AS entity, count(c) AS chunk_count LIMIT 10"):
    print(f"  {row}")
