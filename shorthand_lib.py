import requests
import json
import re

class ShorthandCompressor:
    def __init__(self, model_name="shorthand", ollama_url="http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        
        # Regex patterns for masking
        self.url_pattern = re.compile(r'https?://[^\s<>"]+|www\.[^\s<>"]+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

    def _mask_entities(self, text):
        replacements = {}
        counter = 0

        def replace_match(match, type_prefix):
            nonlocal counter
            original = match.group(0)
            token = f"__{type_prefix}_{counter}__"
            replacements[token] = original
            counter += 1
            return token

        # Mask Emails first
        text = self.email_pattern.sub(lambda m: replace_match(m, "EMAIL"), text)
        # Mask URLs
        text = self.url_pattern.sub(lambda m: replace_match(m, "URL"), text)

        return text, replacements

    def _unmask_entities(self, text, replacements):
        for token, original in replacements.items():
            text = text.replace(token, original)
        return text

    def _query_ollama(self, text):
        # 1. Protection Phase
        masked_text, entity_map = self._mask_entities(text)

        # 2. Compression Phase
        payload = {
            "model": self.model_name,
            "prompt": masked_text, 
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 4096
            }
        }
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            result = response.json().get('response', '').strip()
        except Exception as e:
            return f"[ERROR: {str(e)}]"

        # 3. Restoration Phase
        return self._unmask_entities(result, entity_map)

    def _find_safe_boundary(self, text, limit, floor):
        if len(text) <= limit:
            return len(text)

        search_zone = text[floor:limit]
        sentence_match = list(re.finditer(r'[.!?]\s', search_zone))
        if sentence_match:
            return floor + sentence_match[-1].end()

        last_space = text.rfind(' ', floor, limit)
        if last_space != -1:
            return last_space + 1

        return limit

    def stream_compress(self, input_iterator, chunk_size=6000, overlap_size=500):
        buffer = ""
        chunks_processed = 0  # <--- Logic Fix: Track if we have done work
        
        for line in input_iterator:
            buffer += line
            
            while len(buffer) >= chunk_size:
                cut_point = self._find_safe_boundary(buffer, chunk_size, max(0, chunk_size - 200))
                current_chunk = buffer[:cut_point]
                
                yield self._query_ollama(current_chunk)
                chunks_processed += 1
                
                # Overlap logic
                remaining_text = buffer[cut_point:]
                context_start = max(0, cut_point - overlap_size)
                safe_context_start = self._find_safe_boundary(buffer, context_start, max(0, context_start - 100))
                overlap_text = buffer[safe_context_start:cut_point]
                
                buffer = overlap_text + remaining_text

        # Cleanup Phase
        if buffer.strip():
            # If we haven't processed ANY chunks, we MUST process the buffer (Short Input case)
            if chunks_processed == 0:
                yield self._query_ollama(buffer)
            
            # If we HAVE processed chunks, only process if the remainder is significant
            # (i.e., bigger than the overlap artifact we just carried over)
            elif len(buffer) > overlap_size * 1.1:
                yield self._query_ollama(buffer)
