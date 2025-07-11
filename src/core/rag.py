"""
RAG (Retrieval-Augmented Generation) system for Alex Persona AI Chatbot.

Handles conversation parsing, embedding generation, vector storage, and similarity search
using OpenAI embeddings and FAISS for efficient retrieval.
"""

import asyncio
import pickle
from typing import Dict, List, Optional

import faiss
import numpy as np
from openai import AsyncOpenAI

from .config import config
from .models import ConversationChunk, PersonaContext
from .utils import (chunk_text_by_tokens, extract_alex_communication_patterns,
                    is_alex_speaker, load_conversation_files,
                    parse_markdown_conversation)


class ConversationRAG:
    """RAG system for conversation context retrieval and persona analysis."""

    def __init__(self, openai_client: Optional[AsyncOpenAI] = None):
        """
        Initialize the RAG system.

        Args:
            openai_client: Optional OpenAI client, uses config default if None
        """
        self.client = openai_client or config.get_openai_client()
        self.vector_store_path = config.vector_store_path
        self.conversation_path = config.conversation_data_path

        # Vector store components
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: List[ConversationChunk] = []
        self.chunk_map: Dict[int, ConversationChunk] = {}

        # Cache for embeddings to avoid re-computation
        self._embedding_cache: Dict[str, List[float]] = {}

    async def initialize(self, force_rebuild: bool = False) -> None:
        """
        Initialize the RAG system by loading or creating vector store.

        Args:
            force_rebuild: If True, rebuild the vector store from scratch
        """
        if force_rebuild or not self._vector_store_exists():
            await self._build_vector_store()
        else:
            await self._load_vector_store()

    async def similarity_search(self, query: str, k: int = 5) -> List[ConversationChunk]:
        """
        Perform similarity search to find relevant conversation chunks.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of most relevant ConversationChunk objects
        """
        if self.index is None or not self.chunks:
            await self.initialize()

        # Generate embedding for the query
        query_embedding = await self._get_embedding(query)

        # Perform similarity search
        query_vector = np.array([query_embedding], dtype=np.float32)
        scores, indices = self.index.search(query_vector, min(k, len(self.chunks)))

        # Return corresponding chunks
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx in self.chunk_map and score > 0.1:  # Minimum similarity threshold
                chunk = self.chunk_map[idx]
                results.append(chunk)

        return results

    async def analyze_persona_context(self, retrieved_chunks: List[ConversationChunk]) -> PersonaContext:
        """
        Analyze retrieved chunks to extract Alex's persona characteristics.

        Args:
            retrieved_chunks: Chunks retrieved from similarity search

        Returns:
            PersonaContext with extracted persona elements
        """
        # Filter for Alex's chunks
        alex_chunks = [chunk for chunk in retrieved_chunks if is_alex_speaker(chunk.speaker)]

        # Extract communication patterns
        communication_patterns = extract_alex_communication_patterns(alex_chunks)

        # Extract technical expertise areas
        technical_expertise = self._extract_technical_expertise(alex_chunks)

        # Extract decision patterns
        decision_patterns = self._extract_decision_patterns(alex_chunks)

        # Extract personality traits
        personality_traits = self._extract_personality_traits(alex_chunks)

        return PersonaContext(
            communication_style=communication_patterns,
            technical_expertise=technical_expertise,
            decision_patterns=decision_patterns,
            personality_traits=personality_traits,
            relevant_chunks=alex_chunks
        )

    async def _build_vector_store(self) -> None:
        """Build the vector store from conversation files."""
        print("Building vector store from conversations...")

        # Parse all conversation files
        conversation_files = load_conversation_files(self.conversation_path)
        all_chunks = []

        for file_path in conversation_files:
            chunks = parse_markdown_conversation(file_path)
            all_chunks.extend(chunks)

        print(f"Parsed {len(all_chunks)} conversation chunks from {len(conversation_files)} files")

        # Generate embeddings for all chunks
        embeddings = []
        valid_chunks = []

        for i, chunk in enumerate(all_chunks):
            # Process content in smaller pieces if needed
            text_chunks = chunk_text_by_tokens(chunk.content, config.chunk_size, config.chunk_overlap)

            for text_chunk in text_chunks:
                try:
                    embedding = await self._get_embedding(text_chunk)
                    embeddings.append(embedding)

                    # Create a new chunk for each text segment
                    chunk_copy = ConversationChunk(
                        id=f"{chunk.id}_{len(valid_chunks)}",
                        speaker=chunk.speaker,
                        content=text_chunk,
                        metadata=chunk.metadata,
                        timestamp=chunk.timestamp,
                        file_source=chunk.file_source,
                        embedding=embedding
                    )
                    valid_chunks.append(chunk_copy)

                    # Rate limiting - small delay between API calls
                    await asyncio.sleep(0.1)

                except Exception as e:
                    print(f"Error generating embedding for chunk {chunk.id}: {e}")
                    continue

        if not embeddings:
            raise ValueError("No valid embeddings generated")

        # Create FAISS index
        embedding_dim = len(embeddings[0])
        self.index = faiss.IndexFlatIP(embedding_dim)  # Inner product for cosine similarity

        # Normalize embeddings for cosine similarity
        embeddings_array = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings_array)

        # Add to index
        self.index.add(embeddings_array)

        # Store chunks and mapping
        self.chunks = valid_chunks
        self.chunk_map = {i: chunk for i, chunk in enumerate(valid_chunks)}

        # Save vector store
        await self._save_vector_store()

        print(f"Vector store built with {len(valid_chunks)} chunks")

    async def _save_vector_store(self) -> None:
        """Save the vector store to disk."""
        # Save FAISS index
        index_path = self.vector_store_path / "index.faiss"
        faiss.write_index(self.index, str(index_path))

        # Save chunks and metadata
        chunks_path = self.vector_store_path / "chunks.pkl"
        with open(chunks_path, 'wb') as f:
            pickle.dump({
                'chunks': self.chunks,
                'chunk_map': self.chunk_map
            }, f)

        print(f"Vector store saved to {self.vector_store_path}")

    async def _load_vector_store(self) -> None:
        """Load the vector store from disk."""
        try:
            # Load FAISS index
            index_path = self.vector_store_path / "index.faiss"
            self.index = faiss.read_index(str(index_path))

            # Load chunks and metadata
            chunks_path = self.vector_store_path / "chunks.pkl"
            with open(chunks_path, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.chunk_map = data['chunk_map']

            print(f"Vector store loaded with {len(self.chunks)} chunks")

        except Exception as e:
            print(f"Error loading vector store: {e}")
            await self._build_vector_store()

    def _vector_store_exists(self) -> bool:
        """Check if vector store files exist."""
        index_path = self.vector_store_path / "index.faiss"
        chunks_path = self.vector_store_path / "chunks.pkl"
        return index_path.exists() and chunks_path.exists()

    async def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text with caching.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Check cache first
        cache_key = text[:100]  # Use first 100 chars as cache key
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]

        try:
            response = await self.client.embeddings.create(
                model=config.embedding_model,
                input=text
            )
            embedding = response.data[0].embedding

            # Cache the result
            self._embedding_cache[cache_key] = embedding

            return embedding

        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def _extract_technical_expertise(self, chunks: List[ConversationChunk]) -> List[str]:
        """Extract technical expertise areas from Alex's chunks."""
        expertise_areas = set()

        for chunk in chunks:
            content_lower = chunk.content.lower()

            # AI/ML expertise
            if any(term in content_lower for term in ['ai', 'rag', 'llm', 'openai', 'azure', 'agentic']):
                expertise_areas.add("AI/ML and RAG platforms")

            # Platform engineering
            if any(term in content_lower for term in ['platform', 'api', 'service', 'architecture']):
                expertise_areas.add("Platform engineering and architecture")

            # Microsoft ecosystem
            if any(term in content_lower for term in ['microsoft', 'azure', 'teams', '.net']):
                expertise_areas.add("Microsoft ecosystem and Azure")

            # Engineering leadership
            if any(term in content_lower for term in ['team', 'engineer', 'developer', 'productivity']):
                expertise_areas.add("Engineering team leadership")

            # DevOps and CI/CD
            if any(term in content_lower for term in ['ci/cd', 'deployment', 'devops', 'pipeline']):
                expertise_areas.add("DevOps and continuous deployment")

        return list(expertise_areas)

    def _extract_decision_patterns(self, chunks: List[ConversationChunk]) -> List[str]:
        """Extract decision-making patterns from Alex's chunks."""
        patterns = set()

        for chunk in chunks:
            content_lower = chunk.content.lower()

            # Data-driven decisions
            if any(term in content_lower for term in ['metric', 'data', 'measure', 'quantify']):
                patterns.add("Data-driven and metrics-focused decision making")

            # Collaborative approach
            if any(term in content_lower for term in ['collaborate', 'partner', 'stakeholder', 'team']):
                patterns.add("Collaborative and stakeholder-inclusive approach")

            # User-centric
            if any(term in content_lower for term in ['user', 'customer', 'experience', 'productivity']):
                patterns.add("User-centric and experience-focused")

            # Strategic thinking
            if any(term in content_lower for term in ['strategy', 'roadmap', 'vision', 'long-term']):
                patterns.add("Strategic and long-term thinking")

        return list(patterns)

    def _extract_personality_traits(self, chunks: List[ConversationChunk]) -> List[str]:
        """Extract personality traits from Alex's chunks."""
        traits = set()

        for chunk in chunks:
            content_lower = chunk.content.lower()

            # Detail-oriented
            if len(chunk.content) > 200 and any(term in content_lower for term in ['specific', 'detail', 'example']):
                traits.add("Detail-oriented and thorough")

            # Mission-driven
            if any(term in content_lower for term in ['mission', 'purpose', 'goal', 'impact']):
                traits.add("Mission-driven and impact-focused")

            # Inclusive leadership
            if any(term in content_lower for term in ['mentor', 'promote', 'support', 'inclusive']):
                traits.add("Inclusive and development-focused leader")

            # Innovation-minded
            if any(term in content_lower for term in ['innovation', 'new', 'advance', 'cutting-edge']):
                traits.add("Innovation-minded and forward-thinking")

        return list(traits)
