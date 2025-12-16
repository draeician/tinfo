import requests
import json
import re

class ShorthandCompressor:
    def __init__(self, model_name="shorthand", ollama_url="http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.ollama_url = ollama_url

    def _query_ollama(self, text):
        payload = {
            "model": self.model_name,
            "prompt": text, 
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096  # Bumped to ensure room for input + output
            }
        }
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json().get('response', '').strip()
        except Exception as e:
            return f"[ERROR: {str(e)}]"

    def _find_safe_boundary(self, text, limit, floor):
        """
        Finds the best place to cut the text.
        Priority 1: A period followed by space (Sentence end) near the limit.
        Priority 2: A newline.
        Priority 3: A space (Word end).
        Fallback: Hard cut (if a single massive word exceeds the limit).
        """
        if len(text) <= limit:
            return len(text)

        # Look for sentence endings (.!?) between floor and limit
        search_zone = text[floor:limit]
        
        # Regex for sentence boundary (period/punc followed by space or end of string)
        # We search from the RIGHT side of the zone to get the biggest chunk possible
        sentence_match = list(re.finditer(r'[.!?]\s', search_zone))
        if sentence_match:
            # Cut after the punctuation
            return floor + sentence_match[-1].end()

        # Fallback: Look for the last space
        last_space = text.rfind(' ', floor, limit)
        if last_space != -1:
            return last_space + 1 # Include the space in the first chunk

        # Fallback: Hard limit
        return limit

    def stream_compress(self, input_iterator, chunk_size=6000, overlap_size=500):
        buffer = ""
        
        for line in input_iterator:
            buffer += line
            
            # While we have enough data to form a chunk
            while len(buffer) >= chunk_size:
                # 1. Find a safe cut point (don't cut words in half)
                # We look for a boundary between (chunk_size - 100) and chunk_size
                cut_point = self._find_safe_boundary(buffer, chunk_size, max(0, chunk_size - 200))
                
                # 2. Slice the main chunk
                current_chunk = buffer[:cut_point]
                
                # 3. Process
                compressed = self._query_ollama(current_chunk)
                yield compressed
                
                # 4. Handle Overlap
                # We need to keep some context for the NEXT chunk.
                # But we also don't want to cut the overlap in half.
                remaining_text = buffer[cut_point:]
                
                # Calculate how much to "rewind" to get context
                # We want the last 'overlap_size' chars of what we just processed
                context_start = max(0, cut_point - overlap_size)
                
                # But ensure 'context_start' is also a safe word boundary
                # so the overlap doesn't start with "ccubus"
                safe_context_start = self._find_safe_boundary(buffer, context_start, max(0, context_start - 100))
                
                overlap_text = buffer[safe_context_start:cut_point]
                
                # New buffer = Overlap + Remaining
                buffer = overlap_text + remaining_text

        # Process leftovers
        if buffer.strip():
            # If the leftover is mostly just the overlap we've already seen, skip it.
            # Simple heuristic: if leftover is smaller than overlap * 1.1, it's probably redundant.
            if len(buffer) > overlap_size * 1.1:
                yield self._query_ollama(buffer)
