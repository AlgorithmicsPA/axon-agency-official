import re
from pathlib import Path
from typing import List, Tuple
from bs4 import BeautifulSoup
import httpx
from loguru import logger


class DocumentProcessor:
    def __init__(self, max_chunk_size: int = 1024, overlap: int = 128):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    async def process_pdf(self, file_path: Path) -> List[Tuple[str, dict]]:
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(str(file_path))
            chunks = []
            
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    page_chunks = self.split_text(text, {"page": page_num + 1})
                    chunks.extend(page_chunks)
            
            logger.info(f"Processed PDF: {len(chunks)} chunks from {len(reader.pages)} pages")
            return chunks
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return []
    
    async def process_url(self, url: str) -> List[Tuple[str, dict]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0, follow_redirects=True)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
                    tag.decompose()
                
                text = soup.get_text()
                text = re.sub(r'\n\s*\n', '\n\n', text)
                text = text.strip()
                
                chunks = self.split_text(text, {"url": url})
                logger.info(f"Processed URL: {len(chunks)} chunks from {url}")
                return chunks
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            return []
    
    async def process_markdown(self, file_path: Path) -> List[Tuple[str, dict]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            chunks = self.split_text(text, {"file": str(file_path)})
            logger.info(f"Processed Markdown: {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error processing Markdown: {e}")
            return []
    
    async def process_text(self, file_path: Path) -> List[Tuple[str, dict]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            chunks = self.split_text(text, {"file": str(file_path)})
            logger.info(f"Processed text file: {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error processing text file: {e}")
            return []
    
    def split_text(self, text: str, meta: dict = None) -> List[Tuple[str, dict]]:
        if meta is None:
            meta = {}
        
        text = self.clean_text(text)
        
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence.split())
            
            if current_size + sentence_size > self.max_chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append((chunk_text, meta.copy()))
                
                overlap_words = []
                overlap_size = 0
                for sent in reversed(current_chunk):
                    sent_size = len(sent.split())
                    if overlap_size + sent_size <= self.overlap:
                        overlap_words.insert(0, sent)
                        overlap_size += sent_size
                    else:
                        break
                
                current_chunk = overlap_words
                current_size = overlap_size
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append((chunk_text, meta.copy()))
        
        return chunks
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def estimate_tokens(self, text: str) -> int:
        return len(text.split())


document_processor = DocumentProcessor()
