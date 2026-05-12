import boto3, json

session = boto3.Session(profile_name="gapv50k", region_name="ap-southeast-1")
neptune = session.client("neptune-graph")
graph_id = "g-0keuwoev4a"

def query(q):
    resp = neptune.execute_query(graphIdentifier=graph_id, queryString=q, language="OPEN_CYPHER")
    return json.loads(resp["payload"].read()).get("results", [])

print("=== Entity types ===")
for row in query("MATCH (n) RETURN labels(n) AS label, count(*) AS cnt ORDER BY cnt DESC LIMIT 10"):
    print(f"  {row}")

print("\n=== Relation types ===")
for row in query("MATCH ()-[r]->() RETURN type(r) AS rel, count(*) AS cnt ORDER BY cnt DESC LIMIT 20"):
    print(f"  {row}")

print("\n=== Sample drug entities (first 20) ===")
for row in query("MATCH (n:Entity) WHERE n.value CONTAINS 'dexamethasone' OR n.value CONTAINS 'tocilizumab' OR n.value CONTAINS 'remdesivir' OR n.value CONTAINS 'nirmatrelvir' OR n.value CONTAINS 'heparin' OR n.value CONTAINS 'baricitinib' RETURN n.value AS drug LIMIT 20"):
    print(f"  {row}")

print("\n=== Sample relations involving drugs (first 20) ===")
for row in query("MATCH (a:Entity)-[r]->(b:Entity) WHERE a.value CONTAINS 'nirmatrelvir' OR a.value CONTAINS 'ritonavir' RETURN a.value AS from_entity, type(r) AS relation, b.value AS to_entity LIMIT 20"):
    print(f"  {row}")

print("\n=== Drug interaction relations ===")
for row in query("MATCH (a:Entity)-[r]->(b:Entity) WHERE type(r) CONTAINS 'interact' OR type(r) CONTAINS 'contraindic' OR type(r) CONTAINS 'inhibit' OR type(r) CONTAINS 'reduce' RETURN a.value AS from_e, type(r) AS rel, b.value AS to_e LIMIT 30"):
    print(f"  {row}")

print("\n=== Relations from corticosteroids ===")
for row in query("MATCH (a:Entity)-[r]->(b:Entity) WHERE a.value CONTAINS 'corticosteroid' OR a.value CONTAINS 'dexamethasone' RETURN a.value AS from_e, type(r) AS rel, b.value AS to_e LIMIT 20"):
    print(f"  {row}")
