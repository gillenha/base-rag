"""
Semantic-Aware Chunking System for Ramit Sethi Content

This module implements intelligent chunking that preserves framework coherence,
maintains case study integrity, and respects conceptual boundaries in Ramit's content.
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from langchain.schema.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .token_utils import count_tokens, chunk_text_by_tokens, validate_token_limit, truncate_to_token_limit

class ChunkType(Enum):
    MACRO = "macro"        # Complete frameworks or case studies
    MICRO = "micro"        # Specific tactical steps or concepts
    CONTEXT = "context"    # Overlapping sections for continuity

class ContentBoundary(Enum):
    FRAMEWORK_START = "framework_start"
    FRAMEWORK_END = "framework_end"
    CASE_STUDY_START = "case_study_start"
    CASE_STUDY_END = "case_study_end"
    TACTICAL_SEQUENCE = "tactical_sequence"
    SECTION_BREAK = "section_break"
    DIALOGUE_EXCHANGE = "dialogue_exchange"

@dataclass
class ChunkBoundary:
    """Represents a potential chunk boundary with metadata"""
    position: int
    boundary_type: ContentBoundary
    confidence: float
    context: str = ""

@dataclass
class SemanticChunk:
    """Enhanced chunk with semantic metadata"""
    content: str
    chunk_type: ChunkType
    start_pos: int
    end_pos: int
    metadata: Dict[str, Any]
    quality_score: float = 0.0
    conceptual_completeness: float = 0.0
    framework_coherence: float = 0.0
    tactical_integrity: float = 0.0

class SemanticChunker:
    """
    Semantic-aware chunker that preserves Ramit's frameworks and conceptual coherence
    """
    
    def __init__(self, 
                 macro_chunk_tokens: int = 1500,  # Changed to token-based
                 micro_chunk_tokens: int = 800,   # Changed to token-based
                 overlap_tokens: int = 150,       # Changed to token-based
                 max_chunk_tokens: int = 2000):   # Hard limit for any chunk
        self.macro_chunk_tokens = macro_chunk_tokens
        self.micro_chunk_tokens = micro_chunk_tokens
        self.overlap_tokens = overlap_tokens
        self.max_chunk_tokens = max_chunk_tokens
        
        # Keep character-based limits as fallback
        self.macro_chunk_size = macro_chunk_tokens * 4  # Rough conversion
        self.micro_chunk_size = micro_chunk_tokens * 4
        self.overlap_size = overlap_tokens * 4
        
        # Initialize boundary detection patterns
        self.boundary_patterns = self._initialize_boundary_patterns()
        self.framework_indicators = self._initialize_framework_indicators()
        self.case_study_indicators = self._initialize_case_study_indicators()
        self.tactical_indicators = self._initialize_tactical_indicators()
        
    def _initialize_boundary_patterns(self) -> Dict[ContentBoundary, List[str]]:
        """Initialize patterns for detecting content boundaries"""
        return {
            ContentBoundary.FRAMEWORK_START: [
                r"(?i)the\s+(.+?)\s+framework",
                r"(?i)here's\s+how\s+(.+?)\s+works",
                r"(?i)the\s+(.+?)\s+process",
                r"(?i)let\s+me\s+walk\s+you\s+through",
                r"(?i)step\s+1|first\s+step",
                r"(?i)here\s+are\s+the\s+(\d+)\s+steps",
                r"(?i)the\s+anatomy\s+of",
                r"(?i)components?\s+of"
            ],
            ContentBoundary.FRAMEWORK_END: [
                r"(?i)that's\s+the\s+(.+?)\s+framework",
                r"(?i)so\s+that's\s+how\s+(.+?)\s+works",
                r"(?i)those\s+are\s+the\s+steps",
                r"(?i)and\s+that's\s+it",
                r"(?i)to\s+summarize",
                r"(?i)in\s+summary"
            ],
            ContentBoundary.CASE_STUDY_START: [
                r"(?i)let\s+me\s+tell\s+you\s+about",
                r"(?i)here's\s+a\s+story",
                r"(?i)student\s+story",
                r"(?i)for\s+example",
                r"(?i)one\s+of\s+our\s+students",
                r"(?i)real\s+example",
                r"(?i)case\s+study",
                r"(?i)behind\s+the\s+scenes"
            ],
            ContentBoundary.CASE_STUDY_END: [
                r"(?i)that's\s+the\s+lesson",
                r"(?i)the\s+point\s+is",
                r"(?i)what\s+can\s+we\s+learn",
                r"(?i)the\s+takeaway",
                r"(?i)so\s+remember"
            ],
            ContentBoundary.TACTICAL_SEQUENCE: [
                r"(?i)step\s+\d+",
                r"(?i)first,?\s+",
                r"(?i)second,?\s+",
                r"(?i)third,?\s+",
                r"(?i)next,?\s+",
                r"(?i)then,?\s+",
                r"(?i)finally,?\s+",
                r"(?i)\d+\.\s+[A-Z]"
            ],
            ContentBoundary.SECTION_BREAK: [
                r"\n\s*\n\s*[A-Z][A-Z\s]+\n",  # All caps headings
                r"\n\s*=+\s*\n",                # Separator lines
                r"\n\s*-{3,}\s*\n",             # Dash separators
                r"(?i)transcript",
                r"(?i)new\s+topic",
                r"(?i)moving\s+on"
            ],
            ContentBoundary.DIALOGUE_EXCHANGE: [
                r"(?i)ramit:",
                r"(?i)student:",
                r"(?i)[A-Z][a-z]+:"  # Name followed by colon
            ]
        }
    
    def _initialize_framework_indicators(self) -> List[str]:
        """Framework-specific terminology that should stay together"""
        return [
            "customer research", "mind reading", "customer interviews",
            "winning offer", "irresistible offer", "anatomy of",
            "authentic selling", "sales process", "objection handling",
            "profit playbook", "business model", "revenue streams",
            "invisible scripts", "money dials", "limiting beliefs"
        ]
    
    def _initialize_case_study_indicators(self) -> List[str]:
        """Indicators of case study content that should be preserved"""
        return [
            "student story", "real example", "case study", "teardown",
            "makeover", "behind the scenes", "success story",
            "before and after", "transformation"
        ]
    
    def _initialize_tactical_indicators(self) -> List[str]:
        """Indicators of tactical content that should stay sequential"""
        return [
            "step by step", "exact script", "word for word",
            "copy and paste", "template", "checklist", "process"
        ]
    
    def chunk_document(self, document: Document) -> List[SemanticChunk]:
        """
        Chunk a document using semantic awareness
        
        Args:
            document: Document to chunk
            
        Returns:
            List of semantic chunks with enhanced metadata
        """
        content = document.page_content
        boundaries = self._detect_boundaries(content)
        
        # Create hierarchical chunks
        macro_chunks = self._create_macro_chunks(content, boundaries)
        micro_chunks = self._create_micro_chunks(macro_chunks)
        context_chunks = self._create_context_chunks(macro_chunks)
        
        # Combine and score chunks
        all_chunks = macro_chunks + micro_chunks + context_chunks
        
        # Score chunk quality
        for chunk in all_chunks:
            chunk.quality_score = self._calculate_quality_score(chunk)
            chunk.conceptual_completeness = self._evaluate_conceptual_completeness(chunk)
            chunk.framework_coherence = self._evaluate_framework_coherence(chunk)
            chunk.tactical_integrity = self._evaluate_tactical_integrity(chunk)
        
        # Convert to Document objects with enhanced metadata
        return self._chunks_to_documents(all_chunks, document.metadata)
    
    def _detect_boundaries(self, content: str) -> List[ChunkBoundary]:
        """Detect semantic boundaries in content"""
        boundaries = []
        
        for boundary_type, patterns in self.boundary_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.MULTILINE):
                    boundaries.append(ChunkBoundary(
                        position=match.start(),
                        boundary_type=boundary_type,
                        confidence=self._calculate_boundary_confidence(match, content),
                        context=content[max(0, match.start()-50):match.end()+50]
                    ))
        
        # Sort by position
        boundaries.sort(key=lambda x: x.position)
        
        # Remove low-confidence boundaries
        boundaries = [b for b in boundaries if b.confidence > 0.3]
        
        return boundaries
    
    def _calculate_boundary_confidence(self, match, content: str) -> float:
        """Calculate confidence score for a boundary detection"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for certain contexts
        context = content[max(0, match.start()-100):match.end()+100].lower()
        
        # Higher confidence if surrounded by whitespace
        if match.start() > 0 and content[match.start()-1] in '\\n\\r':
            confidence += 0.2
        
        # Higher confidence if followed by content that looks like a continuation
        if any(indicator in context for indicator in self.framework_indicators):
            confidence += 0.2
        
        # Lower confidence if in the middle of a sentence
        if match.start() > 0 and content[match.start()-1] not in '.!?\\n\\r':
            confidence -= 0.2
        
        return min(1.0, max(0.0, confidence))
    
    def _create_macro_chunks(self, content: str, boundaries: List[ChunkBoundary]) -> List[SemanticChunk]:
        """Create macro chunks based on major boundaries"""
        chunks = []
        current_start = 0
        
        # Find major section boundaries
        major_boundaries = [b for b in boundaries if b.boundary_type in [
            ContentBoundary.FRAMEWORK_START,
            ContentBoundary.FRAMEWORK_END,
            ContentBoundary.CASE_STUDY_START,
            ContentBoundary.CASE_STUDY_END,
            ContentBoundary.SECTION_BREAK
        ]]
        
        for boundary in major_boundaries:
            if boundary.position - current_start > 200:  # Minimum chunk size
                chunk_content = content[current_start:boundary.position].strip()
                if chunk_content:
                    # Validate and potentially split by token limits
                    chunk_token_count = count_tokens(chunk_content)
                    
                    if chunk_token_count <= self.max_chunk_tokens:
                        # Chunk is within limits
                        chunks.append(SemanticChunk(
                            content=chunk_content,
                            chunk_type=ChunkType.MACRO,
                            start_pos=current_start,
                            end_pos=boundary.position,
                            metadata={
                                "boundary_type": boundary.boundary_type.value,
                                "token_count": chunk_token_count
                            }
                        ))
                    else:
                        # Chunk exceeds token limit, split it
                        sub_chunks = chunk_text_by_tokens(
                            chunk_content, 
                            max_tokens=self.macro_chunk_tokens,
                            overlap_tokens=self.overlap_tokens
                        )
                        
                        for i, sub_chunk in enumerate(sub_chunks):
                            chunks.append(SemanticChunk(
                                content=sub_chunk,
                                chunk_type=ChunkType.MACRO,
                                start_pos=current_start + i * len(sub_chunk) // len(sub_chunks),
                                end_pos=current_start + (i + 1) * len(sub_chunk) // len(sub_chunks),
                                metadata={
                                    "boundary_type": boundary.boundary_type.value,
                                    "token_count": count_tokens(sub_chunk),
                                    "split_chunk": True,
                                    "split_index": i
                                }
                            ))
                current_start = boundary.position
        
        # Add final chunk
        if current_start < len(content):
            final_content = content[current_start:].strip()
            if final_content:
                chunk_token_count = count_tokens(final_content)
                
                if chunk_token_count <= self.max_chunk_tokens:
                    chunks.append(SemanticChunk(
                        content=final_content,
                        chunk_type=ChunkType.MACRO,
                        start_pos=current_start,
                        end_pos=len(content),
                        metadata={
                            "boundary_type": "document_end",
                            "token_count": chunk_token_count
                        }
                    ))
                else:
                    # Split final chunk if too large
                    sub_chunks = chunk_text_by_tokens(
                        final_content,
                        max_tokens=self.macro_chunk_tokens,
                        overlap_tokens=self.overlap_tokens
                    )
                    
                    for i, sub_chunk in enumerate(sub_chunks):
                        chunks.append(SemanticChunk(
                            content=sub_chunk,
                            chunk_type=ChunkType.MACRO,
                            start_pos=current_start + i * len(sub_chunk) // len(sub_chunks),
                            end_pos=current_start + (i + 1) * len(sub_chunk) // len(sub_chunks),
                            metadata={
                                "boundary_type": "document_end",
                                "token_count": count_tokens(sub_chunk),
                                "split_chunk": True,
                                "split_index": i
                            }
                        ))
        
        return chunks
    
    def _create_micro_chunks(self, macro_chunks: List[SemanticChunk]) -> List[SemanticChunk]:
        """Create micro chunks from macro chunks that are too large"""
        micro_chunks = []
        
        for macro_chunk in macro_chunks:
            # Check token count instead of character count
            chunk_token_count = count_tokens(macro_chunk.content)
            
            if chunk_token_count > self.macro_chunk_tokens:
                # Split by tokens for oversized chunks
                sub_chunks = chunk_text_by_tokens(
                    macro_chunk.content,
                    max_tokens=self.micro_chunk_tokens,
                    overlap_tokens=self.overlap_tokens
                )
                
                current_pos = macro_chunk.start_pos
                
                for i, sub_chunk in enumerate(sub_chunks):
                    # Validate micro chunk token count
                    micro_token_count = count_tokens(sub_chunk)
                    
                    # Ensure even micro chunks don't exceed limits
                    if micro_token_count > self.max_chunk_tokens:
                        sub_chunk = truncate_to_token_limit(sub_chunk, self.max_chunk_tokens)
                        micro_token_count = count_tokens(sub_chunk)
                    
                    micro_chunks.append(SemanticChunk(
                        content=sub_chunk,
                        chunk_type=ChunkType.MICRO,
                        start_pos=current_pos,
                        end_pos=current_pos + len(sub_chunk),
                        metadata={
                            **macro_chunk.metadata,
                            "parent_chunk": f"macro_{macro_chunks.index(macro_chunk)}",
                            "sub_chunk_index": i,
                            "token_count": micro_token_count
                        }
                    ))
                    current_pos += len(sub_chunk)
        
        return micro_chunks
    
    def _create_context_chunks(self, macro_chunks: List[SemanticChunk]) -> List[SemanticChunk]:
        """Create context chunks that overlap between major sections"""
        context_chunks = []
        
        for i in range(len(macro_chunks) - 1):
            current_chunk = macro_chunks[i]
            next_chunk = macro_chunks[i + 1]
            
            # Create overlapping chunk between consecutive macro chunks
            overlap_start = max(0, current_chunk.end_pos - self.overlap_size)
            overlap_end = min(len(current_chunk.content) + len(next_chunk.content), 
                            next_chunk.start_pos + self.overlap_size)
            
            # Get the overlapping content using token-based overlap
            current_tail = current_chunk.content[-(self.overlap_tokens * 4 // 2):]
            next_head = next_chunk.content[:self.overlap_tokens * 4 // 2]
            overlap_content = current_tail + " " + next_head
            
            if len(overlap_content.strip()) > 100:  # Minimum overlap size
                # Validate and truncate context chunk token count
                overlap_token_count = count_tokens(overlap_content.strip())
                
                if overlap_token_count > self.max_chunk_tokens:
                    overlap_content = truncate_to_token_limit(overlap_content.strip(), self.max_chunk_tokens)
                    overlap_token_count = count_tokens(overlap_content)
                
                context_chunks.append(SemanticChunk(
                    content=overlap_content.strip(),
                    chunk_type=ChunkType.CONTEXT,
                    start_pos=overlap_start,
                    end_pos=overlap_end,
                    metadata={
                        "context_between": f"macro_{i}_and_macro_{i+1}",
                        "transition_type": "macro_boundary",
                        "token_count": overlap_token_count
                    }
                ))
        
        return context_chunks
    
    def _calculate_quality_score(self, chunk: SemanticChunk) -> float:
        """Calculate overall quality score for a chunk"""
        scores = []
        
        # Content completeness
        content = chunk.content.lower()
        
        # Check for complete sentences
        sentence_endings = content.count('.') + content.count('!') + content.count('?')
        if sentence_endings > 0:
            scores.append(0.8)
        else:
            scores.append(0.3)
        
        # Check for framework coherence
        framework_terms = sum(1 for term in self.framework_indicators if term in content)
        if framework_terms > 0:
            scores.append(min(1.0, framework_terms * 0.3))
        
        # Check for tactical sequence integrity
        tactical_terms = sum(1 for term in self.tactical_indicators if term in content)
        if tactical_terms > 0:
            scores.append(min(1.0, tactical_terms * 0.3))
        
        # Penalize very short chunks
        if len(chunk.content) < 100:
            scores.append(0.2)
        elif len(chunk.content) < 300:
            scores.append(0.6)
        else:
            scores.append(0.9)
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _evaluate_conceptual_completeness(self, chunk: SemanticChunk) -> float:
        """Evaluate if chunk contains complete conceptual units"""
        content = chunk.content.lower()
        
        # Check for complete thoughts
        complete_indicators = [
            "in summary", "to recap", "the point is", "remember",
            "that's how", "that's why", "so we can see"
        ]
        
        incomplete_indicators = [
            "for example", "such as", "including", "like",
            "but first", "next we'll", "then we"
        ]
        
        complete_score = sum(1 for indicator in complete_indicators if indicator in content)
        incomplete_score = sum(1 for indicator in incomplete_indicators if indicator in content)
        
        # Base score on sentence structure
        sentences = content.split('.')
        complete_sentences = len([s for s in sentences if len(s.strip()) > 20])
        
        if complete_sentences > 0:
            base_score = 0.7
        else:
            base_score = 0.3
        
        # Adjust based on completion indicators
        adjustment = (complete_score - incomplete_score) * 0.1
        return min(1.0, max(0.0, base_score + adjustment))
    
    def _evaluate_framework_coherence(self, chunk: SemanticChunk) -> float:
        """Evaluate if chunk maintains framework coherence"""
        content = chunk.content.lower()
        
        # Count framework-related terms
        framework_count = sum(1 for term in self.framework_indicators if term in content)
        
        # Look for framework structure indicators
        structure_indicators = [
            "step ", "first", "second", "next", "then", "finally",
            "component", "element", "part", "phase"
        ]
        structure_count = sum(1 for indicator in structure_indicators if indicator in content)
        
        # Calculate coherence based on density and structure
        content_length = len(content.split())
        if content_length > 0:
            framework_density = framework_count / content_length * 100
            structure_density = structure_count / content_length * 100
            
            # Higher density indicates better framework coherence
            coherence_score = min(1.0, (framework_density + structure_density) * 2)
        else:
            coherence_score = 0.0
        
        return coherence_score
    
    def _evaluate_tactical_integrity(self, chunk: SemanticChunk) -> float:
        """Evaluate if chunk maintains tactical sequence integrity"""
        content = chunk.content.lower()
        
        # Look for step sequences
        step_pattern = r"step\s+(\d+)"
        steps = re.findall(step_pattern, content)
        
        if len(steps) > 1:
            # Check if steps are sequential
            step_numbers = [int(s) for s in steps]
            is_sequential = all(step_numbers[i] + 1 == step_numbers[i + 1] 
                              for i in range(len(step_numbers) - 1))
            if is_sequential:
                return 0.9
            else:
                return 0.6
        
        # Look for other tactical indicators
        tactical_count = sum(1 for term in self.tactical_indicators if term in content)
        
        # Check for imperative language (action-oriented)
        imperative_indicators = [
            "do this", "try this", "use this", "remember to",
            "make sure", "don't forget", "always", "never"
        ]
        imperative_count = sum(1 for indicator in imperative_indicators if indicator in content)
        
        # Calculate integrity score
        total_indicators = tactical_count + imperative_count
        return min(1.0, total_indicators * 0.2)
    
    def _chunks_to_documents(self, chunks: List[SemanticChunk], base_metadata: Dict[str, Any]) -> List[Document]:
        """Convert semantic chunks to Document objects"""
        documents = []
        
        for i, chunk in enumerate(chunks):
            # Enhance metadata with chunk information
            enhanced_metadata = base_metadata.copy()
            enhanced_metadata.update({
                "chunk_id": f"{chunk.chunk_type.value}_{i}",
                "chunk_type": chunk.chunk_type.value,
                "semantic_quality_score": chunk.quality_score,
                "conceptual_completeness": chunk.conceptual_completeness,
                "framework_coherence": chunk.framework_coherence,
                "tactical_integrity": chunk.tactical_integrity,
                "chunk_length": len(chunk.content),
                **chunk.metadata
            })
            
            documents.append(Document(
                page_content=chunk.content,
                metadata=enhanced_metadata
            ))
        
        return documents

def semantic_split_documents(documents: List[Document], 
                           macro_chunk_tokens: int = 1500,
                           micro_chunk_tokens: int = 800,
                           overlap_tokens: int = 150) -> List[Document]:
    """
    Split documents using semantic-aware chunking
    
    Args:
        documents: List of documents to split
        macro_chunk_tokens: Target token count for macro chunks
        micro_chunk_tokens: Target token count for micro chunks  
        overlap_tokens: Token overlap size for context chunks
        
    Returns:
        List of semantically chunked documents
    """
    chunker = SemanticChunker(
        macro_chunk_tokens=macro_chunk_tokens,
        micro_chunk_tokens=micro_chunk_tokens,
        overlap_tokens=overlap_tokens
    )
    
    all_chunks = []
    for document in documents:
        chunks = chunker.chunk_document(document)
        all_chunks.extend(chunks)
    
    print(f"Semantic chunking: {len(documents)} documents → {len(all_chunks)} semantic chunks")
    
    # Log chunk quality statistics
    if all_chunks:
        avg_quality = sum(float(chunk.metadata.get("semantic_quality_score", 0)) 
                         for chunk in all_chunks) / len(all_chunks)
        avg_completeness = sum(float(chunk.metadata.get("conceptual_completeness", 0)) 
                              for chunk in all_chunks) / len(all_chunks)
        print(f"Average chunk quality: {avg_quality:.2f}")
        print(f"Average conceptual completeness: {avg_completeness:.2f}")
    
    return all_chunks