import json
import hashlib
from datetime import datetime

import chromadb
from chromadb.utils import embedding_functions


class VectorDBManager:
    """
    Persona Memory Store backed by ChromaDB (persistent).
    - Stores persona embeddings + metadata
    - Retrieves similar personas by semantic search
    - Updates persona participation history
    """

    def __init__(self, db_path: str = "./persona_memory_db", collection_name: str = "persona_memory"):
        # Persistent local storage directory
        self.client = chromadb.PersistentClient(path=db_path)

        # Multilingual embedding model
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )

        # Create or load collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    @staticmethod
    def _generate_persona_id(persona_data: dict) -> str:
        """Generate a stable unique ID using MD5 hash of persona JSON."""
        content_str = json.dumps(persona_data, sort_keys=True, ensure_ascii=False)
        return f"pers_{hashlib.md5(content_str.encode('utf-8')).hexdigest()[:12]}"

    @staticmethod
    def _create_embedding_text(persona: dict) -> str:
        """Convert persona fields into a single text string for embedding."""
        parts = []

        # Demographics / role
        if "age" in persona:
            parts.append(f"age {persona.get('age')}")
        if persona.get("role"):
            parts.append(f"role {persona.get('role')}")

        # Traits
        for trait in persona.get("traits", []) or []:
            parts.append(f"trait {trait}")

        # Context
        if persona.get("context"):
            parts.append(f"context {persona.get('context')}")

        # Survey history (if present)
        history = persona.get("survey_history", []) or []
        for topic in history:
            parts.append(f"participated_in {topic}")

        return " | ".join(parts).strip()

    def store_persona(self, persona_data: dict, survey_topic: str) -> dict:
        """Store a single persona into the vector database."""
        try:
            if not isinstance(persona_data, dict):
                return {"status": "error", "error": "persona_data must be a dict"}
            if not survey_topic:
                return {"status": "error", "error": "survey_topic is required"}

            # Ensure persona has an ID
            if "id" not in persona_data or not persona_data["id"]:
                persona_data["id"] = self._generate_persona_id(persona_data)

            persona_id = persona_data["id"]

            metadata = {
                "persona_id": persona_id,
                "name": persona_data.get("name", ""),
                "age": persona_data.get("age", ""),
                "role": persona_data.get("role", ""),
                "created_at": datetime.now().isoformat(),
                "source_survey": survey_topic,
                "traits": json.dumps(persona_data.get("traits", []), ensure_ascii=False),
                "context": persona_data.get("context", ""),
                "survey_history": json.dumps([survey_topic], ensure_ascii=False),
            }

            doc_text = self._create_embedding_text(persona_data)

            self.collection.add(
                documents=[doc_text],
                metadatas=[metadata],
                ids=[persona_id],
            )

            return {
                "status": "success",
                "persona_id": persona_id,
                "message": f"Stored persona: {persona_data.get('name', 'Unknown')}",
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def retrieve_personas(self, query_text: str, topic_filter: str = None, limit: int = 5) -> dict:
        """Retrieve similar personas by semantic search."""
        try:
            if not query_text:
                return {"status": "error", "error": "query_text is required"}

            where_filter = None
            if topic_filter:
                where_filter = {"source_survey": {"$eq": topic_filter}}

            results = self.collection.query(
                query_texts=[query_text],
                n_results=int(limit),
                where=where_filter,
                include=["metadatas", "distances", "documents"],
            )

            personas = []
            if results.get("ids") and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    meta = results["metadatas"][0][i]
                    dist = results["distances"][0][i]
                    personas.append(
                        {
                            "id": meta.get("persona_id"),
                            "name": meta.get("name"),
                            "age": meta.get("age"),
                            "role": meta.get("role"),
                            "traits": json.loads(meta.get("traits", "[]")),
                            "context": meta.get("context", ""),
                            "similarity_score": float(1 - dist),
                            "survey_history": json.loads(meta.get("survey_history", "[]")),
                        }
                    )

            return {
                "status": "success",
                "count": len(personas),
                "personas": personas,
                "query": query_text,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def update_persona_history(self, persona_id: str, survey_topic: str, responses: dict = None) -> dict:
        """Update a persona's participation history and optionally store last responses."""
        try:
            if not persona_id:
                return {"status": "error", "error": "persona_id is required"}
            if not survey_topic:
                return {"status": "error", "error": "survey_topic is required"}

            existing = self.collection.get(ids=[persona_id], include=["metadatas", "documents"])
            if not existing.get("metadatas"):
                return {"status": "error", "error": "persona not found"}

            meta = existing["metadatas"][0]
            doc = existing["documents"][0] if existing.get("documents") else ""

            history = json.loads(meta.get("survey_history", "[]"))
            if survey_topic not in history:
                history.append(survey_topic)

            meta["survey_history"] = json.dumps(history, ensure_ascii=False)
            meta["last_participated"] = datetime.now().isoformat()

            if responses is not None:
                meta["last_survey_responses"] = json.dumps(responses, ensure_ascii=False)

            self.collection.update(
                ids=[persona_id],
                documents=[doc],
                metadatas=[meta],
            )

            return {
                "status": "success",
                "persona_id": persona_id,
                "updated_history": history,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}


# Tool wrappers for OpenAgents (must return JSON string)
memory_manager = VectorDBManager()


def store_persona(persona_data, survey_topic):
    """Store persona into vector DB (returns JSON string)."""
    result = memory_manager.store_persona(persona_data, survey_topic)
    return json.dumps(result, ensure_ascii=False)


def retrieve_personas(query_text, topic_filter=None, limit=5):
    """Retrieve similar personas from vector DB (returns JSON string)."""
    result = memory_manager.retrieve_personas(query_text, topic_filter, limit)
    return json.dumps(result, ensure_ascii=False)


def update_history(persona_id, survey_topic, responses):
    """Update persona participation history (returns JSON string)."""
    result = memory_manager.update_persona_history(persona_id, survey_topic, responses)
    return json.dumps(result, ensure_ascii=False)
