"""Transcription text cleaning utilities."""

from __future__ import annotations

import re
from typing import List

from config import FILLER_WORDS


def remove_filler_words(text: str, filler_words: List[str] | None = None) -> str:
    """
    Remove filler words from transcription text.
    
    Args:
        text: The transcription text to clean
        filler_words: Optional list of filler words. If None, uses config.FILLER_WORDS
        
    Returns:
        Cleaned text with filler words removed
    """
    if filler_words is None:
        filler_words = FILLER_WORDS
    
    if not text or not filler_words:
        return text
    
    # Split into words while preserving whitespace structure
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        if not line.strip():
            cleaned_lines.append(line)
            continue
        
        # Process each line
        words = line.split()
        cleaned_words = []
        
        i = 0
        while i < len(words):
            word = words[i].lower().strip('.,!?;:()[]{}"\'')
            original_word = words[i]
            
            # Check if this word (or word with punctuation) matches a filler word
            is_filler = False
            for filler in filler_words:
                filler_lower = filler.lower()
                
                # Special handling for "a" - only remove if it's standalone and not followed by a noun/article context
                if word == "a" and filler_lower == "a":
                    # Only remove "a" if it's at the start of the line or after punctuation
                    # (likely a filler "a" rather than an article)
                    prev_text = ' '.join(cleaned_words).lower() if cleaned_words else ''
                    is_at_start = i == 0 or not prev_text or prev_text[-1] in '.!?;:'
                    # Also check if next word suggests it's not an article (like another filler)
                    next_is_filler = False
                    if i < len(words) - 1:
                        next_word_check = words[i + 1].lower().strip('.,!?;:()[]{}"\'')
                        next_is_filler = any(next_word_check == fw.lower() for fw in filler_words if fw.lower() != "a")
                    
                    if is_at_start or next_is_filler:
                        is_filler = True
                        break
                    # Otherwise, keep "a" as it's likely an article
                    continue
                
                # Exact match (case-insensitive, ignoring punctuation)
                if word == filler_lower:
                    is_filler = True
                    break
                # Check for multi-word fillers (like "you know")
                if ' ' in filler_lower and i < len(words) - 1:
                    next_word = words[i + 1].lower().strip('.,!?;:()[]{}"\'')
                    if f"{word} {next_word}" == filler_lower:
                        is_filler = True
                        i += 1  # Skip next word too
                        break
            
            if not is_filler:
                cleaned_words.append(original_word)
            
            i += 1
        
        # Reconstruct line with original spacing
        if cleaned_words:
            cleaned_line = ' '.join(cleaned_words)
            # Preserve trailing punctuation/spacing from original line
            if line.endswith(' ') or line.endswith('\t'):
                cleaned_line += line[-1]
            cleaned_lines.append(cleaned_line)
        else:
            # If all words were removed, keep empty line structure
            cleaned_lines.append('')
    
    result = '\n'.join(cleaned_lines)
    
    # Clean up multiple spaces that might result from removal
    result = re.sub(r' +', ' ', result)
    # Clean up spaces before punctuation
    result = re.sub(r' +([.,!?;:])', r'\1', result)
    # Clean up multiple newlines (keep at most 2)
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    return result.strip()

