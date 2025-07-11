"""
Tests for RAG system functionality.

Tests conversation parsing, embedding generation, vector storage, and similarity search.
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.core.models import ConversationChunk, PersonaContext
from src.core.rag import ConversationRAG


class TestConversationRAG:
    """Test RAG system functionality."""

    @pytest.fixture
    def mock_rag_system(self, mock_openai_client, temp_dir):
        """Create a mock RAG system for testing."""
        with patch('src.core.rag.config') as mock_config:
            mock_config.vector_store_path = temp_dir / "vectors"
            mock_config.conversation_data_path = temp_dir / "convos"
            mock_config.chunk_size = 100
            mock_config.chunk_overlap = 20

            rag = ConversationRAG(mock_openai_client)
            return rag

    @pytest.mark.asyncio
    async def test_get_embedding_success(self, mock_rag_system):
        """Test successful embedding generation."""
        test_text = "This is a test text for embedding generation."

        embedding = await mock_rag_system._get_embedding(test_text)

        assert isinstance(embedding, list)
        assert len(embedding) == 5  # Based on mock response
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.asyncio
    async def test_get_embedding_caching(self, mock_rag_system):
        """Test that embeddings are cached properly."""
        test_text = "This is a test text for caching."

        # First call should call the API
        embedding1 = await mock_rag_system._get_embedding(test_text)

        # Second call should use cache
        embedding2 = await mock_rag_system._get_embedding(test_text)

        assert embedding1 == embedding2
        # Should only be called once due to caching
        assert mock_rag_system.client.embeddings.create.call_count == 1

    @pytest.mark.asyncio
    async def test_get_embedding_api_error(self, mock_openai_client, temp_dir):
        """Test handling of API errors during embedding generation."""
        mock_openai_client.embeddings.create.side_effect = Exception("API Error")

        rag = ConversationRAG(mock_openai_client)

        with pytest.raises(Exception, match="API Error"):
            await rag._get_embedding("test text")

    @pytest.mark.asyncio
    async def test_similarity_search_empty_index(self, mock_rag_system):
        """Test similarity search with empty index."""
        # Mock empty index state
        mock_rag_system.index = None
        mock_rag_system.chunks = []

        # Should initialize automatically
        with patch.object(mock_rag_system, 'initialize') as mock_init:
            mock_init.return_value = None

            results = await mock_rag_system.similarity_search("test query")

            mock_init.assert_called_once()
            assert results == []

    @pytest.mark.asyncio
    async def test_analyze_persona_context_success(self, mock_rag_system):
        """Test successful persona context analysis."""
        # Create test chunks with Alex's content
        alex_chunks = [
            ConversationChunk(
                id="test1",
                speaker="Alex",
                content="I led a team of 15 engineers building an AI platform that served 60K+ users and saved 1,500 hours weekly.",
                file_source="test.md"
            ),
            ConversationChunk(
                id="test2",
                speaker="Alex",
                content="The platform used Azure OpenAI with comprehensive RAG capabilities and extensible APIs for horizontal services.",
                file_source="test.md"
            ),
            ConversationChunk(
                id="test3",
                speaker="John",  # Non-Alex chunk
                content="That sounds impressive. How did you handle the technical challenges?",
                file_source="test.md"
            )
        ]

        persona_context = await mock_rag_system.analyze_persona_context(alex_chunks)

        assert isinstance(persona_context, PersonaContext)
        assert len(persona_context.relevant_chunks) == 2  # Only Alex's chunks
        assert len(persona_context.technical_expertise) > 0
        assert len(persona_context.communication_style) > 0

    def test_extract_technical_expertise(self, mock_rag_system):
        """Test extraction of technical expertise from chunks."""
        chunks = [
            ConversationChunk(
                id="test1",
                speaker="Alex",
                content="We built a comprehensive RAG platform using Azure OpenAI and implemented agentic AI workflows.",
                file_source="test.md"
            ),
            ConversationChunk(
                id="test2",
                speaker="Alex",
                content="The platform architecture included APIs for Microsoft Teams integration and developer productivity tools.",
                file_source="test.md"
            )
        ]

        expertise = mock_rag_system._extract_technical_expertise(chunks)

        assert isinstance(expertise, list)
        assert any("AI/ML and RAG platforms" in area for area in expertise)
        assert any("Platform engineering and architecture" in area for area in expertise)
        assert any("Microsoft ecosystem and Azure" in area for area in expertise)

    def test_extract_decision_patterns(self, mock_rag_system):
        """Test extraction of decision patterns from chunks."""
        chunks = [
            ConversationChunk(
                id="test1",
                speaker="Alex",
                content="We measured success through specific metrics like engineer-hours saved and user satisfaction scores.",
                file_source="test.md"
            ),
            ConversationChunk(
                id="test2",
                speaker="Alex",
                content="I collaborated closely with stakeholders across engineering teams to understand their needs and priorities.",
                file_source="test.md"
            )
        ]

        patterns = mock_rag_system._extract_decision_patterns(chunks)

        assert isinstance(patterns, list)
        assert any("data-driven" in pattern.lower() for pattern in patterns)
        assert any("collaborative" in pattern.lower() for pattern in patterns)

    def test_extract_personality_traits(self, mock_rag_system):
        """Test extraction of personality traits from chunks."""
        chunks = [
            ConversationChunk(
                id="test1",
                speaker="Alex",
                content="My mission was to improve the daily lives of 15,000 engineers through better developer experience. I believe in providing specific examples and detailed explanations to help teams understand the impact of our platform work.",
                file_source="test.md"
            ),
            ConversationChunk(
                id="test2",
                speaker="Alex",
                content="I mentored team members and helped promote 6 engineers during my tenure, focusing on inclusive leadership and innovation.",
                file_source="test.md"
            )
        ]

        traits = mock_rag_system._extract_personality_traits(chunks)

        assert isinstance(traits, list)
        assert any("detail-oriented" in trait.lower() for trait in traits)
        assert any("mission-driven" in trait.lower() for trait in traits)
        assert any("inclusive" in trait.lower() for trait in traits)
        assert any("innovation" in trait.lower() for trait in traits)

    def test_vector_store_exists(self, mock_rag_system):
        """Test vector store existence checking."""
        # Test when files don't exist
        assert not mock_rag_system._vector_store_exists()

        # Create the files
        mock_rag_system.vector_store_path.mkdir(exist_ok=True)
        (mock_rag_system.vector_store_path / "index.faiss").touch()
        (mock_rag_system.vector_store_path / "chunks.pkl").touch()

        # Test when files exist
        assert mock_rag_system._vector_store_exists()


class TestRAGIntegration:
    """Test RAG system integration scenarios."""

    @pytest.mark.asyncio
    async def test_end_to_end_conversation_processing(self, temp_dir, mock_openai_client, sample_conversation_file):
        """Test end-to-end conversation processing workflow."""
        # Setup conversation directory with sample file
        conversation_dir = temp_dir / "convos"
        conversation_dir.mkdir()

        # Copy sample conversation to conversation directory
        dest_file = conversation_dir / "sample.md"
        dest_file.write_text(sample_conversation_file.read_text())

        with patch('src.core.rag.config') as mock_config:
            mock_config.vector_store_path = temp_dir / "vectors"
            mock_config.conversation_data_path = conversation_dir
            mock_config.chunk_size = 100
            mock_config.chunk_overlap = 20

            # Mock FAISS operations
            with patch('src.core.rag.faiss') as mock_faiss:
                mock_index = Mock()
                mock_faiss.IndexFlatIP.return_value = mock_index
                mock_faiss.normalize_L2 = Mock()

                rag = ConversationRAG(mock_openai_client)

                # Should not raise exceptions
                await rag._build_vector_store()

                # Verify embeddings were generated
                assert mock_openai_client.embeddings.create.call_count > 0

                # Verify chunks were processed
                assert len(rag.chunks) > 0
                assert any("Alex" in chunk.speaker for chunk in rag.chunks)

    @pytest.mark.asyncio
    async def test_similarity_search_with_mock_index(self, temp_dir, mock_openai_client):
        """Test similarity search with mocked FAISS index."""
        with patch('src.core.rag.config') as mock_config:
            mock_config.vector_store_path = temp_dir / "vectors"
            mock_config.conversation_data_path = temp_dir / "convos"

            rag = ConversationRAG(mock_openai_client)

            # Create mock index and chunks
            mock_index = Mock()
            mock_index.search.return_value = ([0.8, 0.7], [[0, 1]])  # scores, indices

            rag.index = mock_index
            rag.chunks = [
                ConversationChunk(
                    id="test1",
                    speaker="Alex",
                    content="Test content 1",
                    file_source="test.md"
                ),
                ConversationChunk(
                    id="test2",
                    speaker="Alex",
                    content="Test content 2",
                    file_source="test.md"
                )
            ]
            rag.chunk_map = {0: rag.chunks[0], 1: rag.chunks[1]}

            results = await rag.similarity_search("test query", k=2)

            assert len(results) == 2
            assert all(isinstance(chunk, ConversationChunk) for chunk in results)
            mock_index.search.assert_called_once()
