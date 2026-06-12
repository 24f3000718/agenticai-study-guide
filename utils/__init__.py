"""
Utilities module for the Academic Assistant.
Contains text processing and CS-specific utilities.
"""

# import and re-export text processing utilities
from utils.text_processing import (
    extract_topics,                  # extracts main academic topics from text
    detect_content_type,             # automatically detects type of content
    extract_key_terms,               # extracts key technical terms with scores
    chunk_by_semantic_boundaries     # splits text by semantic boundaries
)

# import and re-export cs-specific utilities
from utils.cs_utils import (
    detect_code_language,            # detects programming language from code
    extract_code_blocks,             # extracts code blocks from text
    detect_algorithm_type,           # detects algorithm type from description
    analyze_algorithm_complexity,    # analyzes time and space complexity
    extract_algorithm_steps,         # extracts step-by-step algorithm steps
    identify_cs_subject,             # identifies cs subjects from content
    format_code_with_syntax,         # formats code with syntax highlighting
    generate_algorithm_explanation,  # generates comprehensive algorithm explanation
    extract_data_structure_info,     # extracts data structure information
    CodeBlock,                       # dataclass for code block info
    AlgorithmInfo,                   # dataclass for algorithm info
    AlgorithmType                    # enum for algorithm types
)

# define what gets exported when someone does "from utils import *"
__all__ = [
    # text processing
    "extract_topics",
    "detect_content_type",
    "extract_key_terms",
    "chunk_by_semantic_boundaries",
    
    # cs utils
    "detect_code_language",
    "extract_code_blocks",
    "detect_algorithm_type",
    "analyze_algorithm_complexity",
    "extract_algorithm_steps",
    "identify_cs_subject",
    "format_code_with_syntax",
    "generate_algorithm_explanation",
    "extract_data_structure_info",
    "CodeBlock",
    "AlgorithmInfo",
    "AlgorithmType",
]
