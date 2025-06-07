import os 
import logging 
from retry import retry 
from neo4j import GraphDatabase 
import dotenv
import datetime
import bcrypt
import uuid

dotenv.load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)

NODES = ["USER", "MESSAGE", ]

class ChatGraph:
    def __init__(self, uri=NEO4J_URI, user=NEO4J_USERNAME, password=NEO4J_PASSWORD):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.uri = uri
        print(self.uri)
        
    def close(self):
        self.driver.close()

    def hash_password(self, plain_password: str) -> str:
        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

    def get_user_by_username(self, user_name: str):
        query = """
        MATCH (u:USER {username: $username})
        RETURN u.user_id AS user_id, u.username AS username, u.password AS password
        """
        with self.driver.session() as session:
            result = session.run(query,  username=user_name)
            record = result.single()
            return record if record else None
        
    def get_user_by_id(self, user_id: str):
        query = """
        MATCH (u:USER {user_id: $user_id})
        RETURN u.user_id AS user_id, u.username AS username, u.password AS password
        """
        with self.driver.session() as session:
            result = session.run(query, user_id=user_id)
            record = result.single()
            return record if record else None
        
    def verify_user(self, user_name:str, password: str): 
        user = self.get_user_by_username(user_name)
        if user and self.check_password(password, user["password"]):
            return user["user_id"]
        return None

    def create_user(self, user_name:str, password: str):
        user_id = str(uuid.uuid4())
        hashed_password = self.hash_password(password)
        query = """
        CREATE (u:USER {user_id: $user_id, username: $username, password: $hased_password})
        """
        with self.driver.session() as session:
            session.run(query, user_id=user_id, username=user_name, hased_password=hashed_password)
            LOGGER.info(f"User {user_name} created successfully with ID {user_id}")
            
        return user_id
    
    def store_message(self, user_id: str, text: str, role: str):
        timestamp = datetime.datetime.now().isoformat()
        if role == "user":
            query = """
            MATCH (u:USER {user_id: $user_id})
            CREATE (m:MESSAGE {text: $text, role: $role, timestamp: $timestamp})
            CREATE (u)-[:SENT]->(m)
            """
        elif role == "assistant":
            query = """
            MATCH (u:USER {user_id: $user_id})
            CREATE (m:MESSAGE {text: $text, role: $role, timestamp: $timestamp})
            CREATE (m)-[:SENT]->(u)
            """
        
        with self.driver.session() as session:
            session.run(query, user_id=user_id, text=text, role=role, timestamp=timestamp)
            LOGGER.info(f"Message stored for user ID {user_id}")

    def get_user_chat_history(self, user_id: str):
        query = """
        MATCH (u:USER {user_id: $user_id})
        MATCH (m:MESSAGE)
        WHERE (u)-[:SENT]->(m) OR (m)-[:SENT]->(u)
        RETURN m.text AS text, m.role AS role, m.timestamp AS timestamp
        ORDER BY m.timestamp ASC
        """
        with self.driver.session() as session:
            result = session.run(query, user_id=user_id)
            return [{"text": r["text"], "role": r["role"], "timestamp": r["timestamp"]} for r in result]
        

    def update_user_info(self, data, user_id: str):
        query = """
        MATCH (u:USER {user_id: $user_id})
        SET 
            u.name = COALESCE($name, u.name),
            u.age = COALESCE($age, u.age)

        // Update Symptoms
        FOREACH (symptom IN $symptoms |
            MERGE (s:Symptom {name: symptom})
            MERGE (u)-[:HAS_SYMPTOM]->(s)
        )

        // Update Health Conditions
        FOREACH (cond IN $health_conditions |
            MERGE (c:Condition {name: cond})
            MERGE (u)-[:HAS_CONDITION]->(c)
        )

        // Update Family Members
        WITH u, $family_members AS family_members
        UNWIND family_members AS fm
            MERGE (f:FamilyMember {user_id: $user_id, relation: fm.relation})
            SET 
                f.name = COALESCE(fm.name, f.name),
                f.age = COALESCE(fm.age, f.age)
            MERGE (u)-[:RELATED_TO]->(f)

            WITH f, fm
            FOREACH (cond IN COALESCE(fm.condition, []) |
                MERGE (c:Condition {name: cond})
                MERGE (f)-[:HAS_CONDITION]->(c)
            )
            FOREACH (sym IN COALESCE(fm.symptoms, []) |
                MERGE (s:Symptom {name: sym})
                MERGE (f)-[:HAS_SYMPTOM]->(s)
            )
        """
        query_parameters = {
            "user_id": user_id,
            "name": data.get("name"),
            "age": data.get("age"),
            "symptoms": data.get("symptoms", []),
            "health_conditions": data.get("health_conditions", []),
            "family_members": data.get("family_members", []),
        }

        with self.driver.session() as session: 
            session.run(query, **query_parameters)
            LOGGER.info(f"Updated information for user ID {user_id}")


    