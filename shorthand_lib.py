import requests
import json
import textwrap

class ShorthandCompressor:
    def __init__(self, model_name="shorthand", ollama_url="http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.ollama_url = ollama_url

    def _query_ollama(self, text):
        """
        Internal method to hit the local API.
        """
        payload = {
            "model": self.model_name,
            "prompt": text, 
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temp for deterministic notes
                "num_ctx": 2048      # Ensure context window is respected
            }
        }
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            return response.json().get('response', '').strip()
        except Exception as e:
            return f"[ERROR: Compression Failed - {str(e)}]"

    def compress_text(self, text):
        """
        Compresses a single block of text. Use this for short strings.
        """
        return self._query_ollama(text)

    def stream_compress(self, input_iterator, chunk_size=6000, overlap_size=500):
        """
        Generator that processes a massive stream of text in chunks.
        
        Args:
            input_iterator: A file object or iterable of strings.
            chunk_size: Approx characters per chunk (aim for ~1500 tokens).
            overlap_size: How many characters from the previous chunk to replay 
                          to preserve context (e.g. who is speaking).
        
        Yields:
            Compressed string segments.
        """
        buffer = ""
        
        # We accumulate text until we hit the chunk_size
        for line in input_iterator:
            buffer += line
            
            while len(buffer) >= chunk_size:
                # 1. Slice the current chunk
                current_chunk = buffer[:chunk_size]
                
                # 2. Process
                compressed = self._query_ollama(current_chunk)
                yield compressed
                
                # 3. Slide the window:
                # Keep the last 'overlap_size' chars to prepend to the next batch
                # This ensures the model knows the context of the start of the next chunk.
                tail = buffer[chunk_size - overlap_size : chunk_size]
                remaining = buffer[chunk_size:]
                buffer = tail + remaining

        # Process any remaining text in the buffer
        if buffer:
            # If the buffer is just the overlap from the last loop, we might skip it 
            # to avoid duplication, but usually safely processing it is better.
            if len(buffer) > overlap_size:
                yield self._query_ollama(buffer)
