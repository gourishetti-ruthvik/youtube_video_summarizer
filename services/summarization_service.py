"""
AI Summarization service using Google Gemini
"""
from google import genai
from google.genai import types
from typing import List, Dict
import json
import re


class SummarizationService:
    """Service for generating AI summaries using Gemini"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initialize summarization service
        
        Args:
            api_key: Gemini API key
            model_name: Gemini model to use
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
    
    def generate_executive_summary(self, full_text: str, video_title: str = "") -> List[str]:
        """
        Generate executive summary with 5-10 key points
        
        Args:
            full_text: Full transcript text
            video_title: Video title for context
        
        Returns:
            List of summary bullets
        """
        prompt = f"""Analyze this YouTube video transcript and create a concise executive summary.

Video Title: {video_title}

Transcript:
{full_text[:15000]}  

Instructions:
1. Create 5-10 key bullet points that capture the main ideas
2. Each bullet should be specific and actionable
3. Focus on the most important insights and takeaways
4. Keep bullets concise (1-2 sentences each)
5. Only use information explicitly stated in the transcript
6. Do not add external information or speculation

Format your response as a numbered list."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Extract text from new API response
            summary_text = response.text
            
            print(f"✓ Executive summary generated ({len(summary_text)} chars)")
            
            # Parse bullets
            bullets = self._parse_bullets(summary_text)
            return bullets[:10]  # Limit to 10
        
        except Exception as e:
            print(f"✗ Error generating executive summary: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return ["Error generating summary. Please check API key and try again."]
    
    def generate_section_summaries(self, chunks: List[Dict], video_title: str = "") -> List[Dict]:
        """
        Generate summaries for each section/chunk with timestamps
        
        Args:
            chunks: List of transcript chunks
            video_title: Video title for context
        
        Returns:
            List of section summaries with timestamps
        """
        section_summaries = []
        
        print(f"\n=== Generating section summaries for {len(chunks)} chunks ===")
        
        # Process each chunk individually for better accuracy
        for i, chunk in enumerate(chunks):
            print(f"\n  Processing chunk {i+1}/{len(chunks)} at {chunk['timestamp']}...")
            
            prompt = f"""Summarize the following video transcript segment in 2-3 clear, informative sentences.

Video: {video_title}
Timestamp: {chunk['timestamp']}

Transcript Segment:
{chunk['text'][:2500]}

Provide ONLY the summary (no labels, no numbering, just the summary text):"""

            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                # Extract text from response
                summary_text = response.text.strip()
                
                # Clean up the summary
                summary_text = re.sub(r'^\d+[\.\)]\s*', '', summary_text)  # Remove numbering
                summary_text = re.sub(r'^(Summary|Section \d+):?\s*', '', summary_text, flags=re.IGNORECASE)
                
                print(f"    ✓ Generated: {summary_text[:80]}...")
                
                section_summaries.append({
                    'timestamp': chunk['timestamp'],
                    'start_time': chunk['start_time'],
                    'summary': summary_text,
                })
            
            except Exception as e:
                print(f"    ✗ Error: {type(e).__name__}: {e}")
                # Fallback: use first 200 chars
                section_summaries.append({
                    'timestamp': chunk['timestamp'],
                    'start_time': chunk['start_time'],
                    'summary': chunk['text'][:200] + "...",
                })
        
        print(f"\n✓ Generated {len(section_summaries)} section summaries\n")
        return section_summaries
    
    def generate_highlights(self, full_text: str, chunks: List[Dict]) -> List[Dict]:
        """
        Extract 10 quotable highlights with timestamps
        
        Args:
            full_text: Full transcript text
            chunks: List of chunks for timestamp reference
        
        Returns:
            List of highlights with quotes and timestamps
        """
        highlights = []
        
        print(f"\n=== Extracting highlights from {len(chunks)} chunks ===")
        
        # Extract 1 highlight from each chunk (up to 10 total)
        target_chunks = chunks[:10]  # Only process first 10 chunks for highlights
        
        for i, chunk in enumerate(target_chunks):
            print(f"\n  Extracting highlight {i+1}/{len(target_chunks)} from {chunk['timestamp']}...")
            
            prompt = f"""Extract ONE powerful, memorable quote from this video transcript segment.

Timestamp: {chunk['timestamp']}

Transcript:
{chunk['text'][:1500]}

INSTRUCTIONS:
- Select the MOST impactful, quotable statement
- Copy it EXACTLY word-for-word (10-50 words)
- Choose something meaningful, insightful, or memorable
- It should stand alone and make sense out of context

Provide ONLY the quote text (no timestamp, no labels, just the quote):"""

            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                
                # Extract quote
                quote_text = response.text.strip()
                
                # Clean up the quote
                quote_text = quote_text.strip('"\'«»“”')
                quote_text = re.sub(r'^(Quote|Highlight):?\s*', '', quote_text, flags=re.IGNORECASE)
                
                # Only add if it's a reasonable length
                if 10 <= len(quote_text) <= 300:
                    highlights.append({
                        'quote': quote_text,
                        'timestamp': chunk['timestamp'],
                        'start_time': chunk['start_time']
                    })
                    print(f"    ✓ Extracted: {quote_text[:60]}...")
                else:
                    print(f"    ⚠️ Quote length invalid ({len(quote_text)} chars), using fallback")
                    # Fallback: extract first meaningful sentence
                    sentences = chunk['text'].split('. ')
                    for sentence in sentences:
                        if len(sentence) > 20:
                            highlights.append({
                                'quote': sentence.strip() + '.',
                                'timestamp': chunk['timestamp'],
                                'start_time': chunk['start_time']
                            })
                            print(f"    ✓ Fallback: {sentence[:60]}...")
                            break
            
            except Exception as e:
                print(f"    ✗ Error: {type(e).__name__}: {e}")
                # Fallback: use first sentence from chunk
                sentences = chunk['text'].split('. ')
                if sentences:
                    highlights.append({
                        'quote': sentences[0].strip() + '.',
                        'timestamp': chunk['timestamp'],
                        'start_time': chunk['start_time']
                    })
        
        # Sort by timestamp
        highlights.sort(key=lambda x: x.get('start_time', 0))
        
        print(f"\n✓ Generated {len(highlights)} highlights with timestamps\n")
        return highlights
    
    def translate_to_english(self, text: str) -> str:
        """
        Translate text to English using Gemini
        
        Args:
            text: Text to translate
        
        Returns:
            Translated text
        """
        prompt = f"""Translate the following text to English. Maintain the original meaning and structure.

Text:
{text[:10000]}

Provide only the translation, no explanations."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            # Extract text from new API response
            return response.text
        
        except Exception as e:
            print(f"✗ Error translating text: {type(e).__name__}: {e}")
            return text
    
    def answer_question(self, query: str, context_chunks: List[Dict], video_title: str = "") -> Dict:
        """
        Generate an intelligent answer to a user's question based on video context
        
        Args:
            query: User's question
            context_chunks: Relevant transcript chunks from search
            video_title: Video title for context
        
        Returns:
            Dictionary with answer, confidence, and supporting timestamps
        """
        if not context_chunks:
            return {
                'answer': "I couldn't find any relevant information about that in the video.",
                'confidence': 'low',
                'timestamps': []
            }
        
        # Build context from chunks
        context_text = ""
        timestamps = []
        for i, chunk in enumerate(context_chunks[:5], 1):  # Use top 5 chunks
            context_text += f"\n[Timestamp {chunk['timestamp']}]\n{chunk['text']}\n"
            timestamps.append(chunk['timestamp'])
        
        prompt = f"""You are analyzing a YouTube video titled "{video_title}".

User's Question: {query}

Relevant Content from Video:
{context_text}

Instructions:
1. Answer the user's question based ONLY on the information provided above
2. Be specific and cite timestamps when mentioning information
3. If the answer is found, provide a clear, concise response (2-4 sentences)
4. If the information is partially available, explain what you found
5. If the question cannot be answered from the content, say so clearly
6. Quote directly from the transcript when appropriate

Format your response as a natural, helpful answer."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            answer_text = response.text
            
            # Determine confidence based on answer content
            confidence = 'high'
            if 'not' in answer_text.lower() and ('found' in answer_text.lower() or 'mentioned' in answer_text.lower()):
                confidence = 'low'
            elif 'partially' in answer_text.lower() or 'some' in answer_text.lower():
                confidence = 'medium'
            
            print(f"✓ Generated answer for query: {query[:50]}...")
            
            return {
                'answer': answer_text,
                'confidence': confidence,
                'timestamps': timestamps[:3],  # Top 3 most relevant timestamps
            }
        
        except Exception as e:
            print(f"✗ Error generating answer: {type(e).__name__}: {e}")
            return {
                'answer': "Sorry, I encountered an error generating an answer. Please try rephrasing your question.",
                'confidence': 'low',
                'timestamps': []
            }
    
    def _parse_bullets(self, text: str) -> List[str]:
        """Parse numbered or bulleted list into array"""
        lines = text.split('\n')
        bullets = []
        
        for line in lines:
            line = line.strip()
            # Match numbered lists (1. or 1) or bullet points (- or *)
            match = re.match(r'^(\d+[\.\)]\s*|\-\s*|\*\s*)(.*)', line)
            if match:
                bullet_text = match.group(2).strip()
                if bullet_text:
                    bullets.append(bullet_text)
        
        return bullets
    
    def _parse_section_summaries(self, text: str, chunks: List[Dict]) -> List[Dict]:
        """Parse section summaries from response"""
        summaries = []
        
        # Try to extract numbered summaries (1. summary, 2. summary, etc.)
        numbered_pattern = r'^(\d+)[\.\)]\s+'
        lines = text.split('\n')
        
        current_summary = ""
        current_number = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with a number (new summary)
            match = re.match(numbered_pattern, line)
            if match:
                # Save previous summary if exists
                if current_summary and current_summary.strip():
                    summaries.append(current_summary.strip())
                    print(f"      Extracted summary {len(summaries)}: {current_summary.strip()[:60]}...")
                
                # Start new summary (remove the number prefix)
                current_number = int(match.group(1))
                current_summary = re.sub(numbered_pattern, '', line).strip()
            else:
                # Continue current summary (multi-line support)
                if current_summary:
                    current_summary += " " + line
                elif line and not line.startswith('*') and not line.startswith('-'):
                    # First line without number (shouldn't happen but handle it)
                    current_summary = line
        
        # Add last summary
        if current_summary and current_summary.strip():
            summaries.append(current_summary.strip())
            print(f"      Extracted summary {len(summaries)}: {current_summary.strip()[:60]}...")
        
        print(f"    → Total parsed: {len(summaries)} summaries for {len(chunks)} chunks")
        
        # Match summaries to chunks
        result = []
        for i, summary_text in enumerate(summaries):
            if i < len(chunks):
                result.append({
                    'timestamp': chunks[i]['timestamp'],
                    'start_time': chunks[i]['start_time'],
                    'summary': summary_text,
                })
        
        # Fill in any missing summaries with chunk text
        for i in range(len(result), len(chunks)):
            result.append({
                'timestamp': chunks[i]['timestamp'],
                'start_time': chunks[i]['start_time'],
                'summary': chunks[i]['text'][:200] + "...",
            })
        
        return result
    
    def _parse_quotes(self, text: str) -> List[str]:
        """Parse quotes from response"""
        quotes = []
        
        # Find all quoted text
        quote_matches = re.findall(r'"([^"]+)"', text)
        quotes.extend(quote_matches)
        
        # Also try numbered format without quotes
        lines = text.split('\n')
        for line in lines:
            match = re.match(r'^\d+[\.\)]\s*(.+)', line)
            if match:
                quote_text = match.group(1).strip().strip('"')
                if quote_text and quote_text not in quotes:
                    quotes.append(quote_text)
        
        return quotes
    
    def _parse_highlights_with_timestamps(self, text: str, chunks: List[Dict]) -> List[Dict]:
        """Parse highlights that include timestamps in the format [HH:MM:SS] or [MM:SS]"""
        highlights = []
        lines = text.split('\n')
        
        print(f"    Parsing {len(lines)} lines for highlights pattern...")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for pattern: [timestamp] "quote"
            # Match formats like [00:10], [05:23], [1:23:45]
            match = re.search(r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*["\']?([^"\']+)["\']?', line)
            
            if match:
                timestamp_str = match.group(1)
                quote_text = match.group(2).strip()
                
                # Clean quote
                quote_text = quote_text.strip('"\'«»“”')
                
                # Skip very short quotes
                if len(quote_text) < 15:
                    print(f"      Skipping short: {quote_text}")
                    continue
                
                print(f"      Found: [{timestamp_str}] {quote_text[:50]}...")
                
                # Find the matching chunk by timestamp
                matching_chunk = None
                for chunk in chunks:
                    if chunk['timestamp'] == timestamp_str or chunk['timestamp'].startswith(timestamp_str):
                        matching_chunk = chunk
                        break
                
                # If no exact match, try fuzzy matching the quote to chunks
                if not matching_chunk:
                    matching_chunk = self._find_best_matching_chunk(quote_text, chunks)
                
                if matching_chunk:
                    highlights.append({
                        'quote': quote_text,
                        'timestamp': matching_chunk['timestamp'],
                        'start_time': matching_chunk['start_time'],
                    })
                    print(f"    ✓ Matched quote to [{matching_chunk['timestamp']}]: {quote_text[:60]}...")
            else:
                # Try to extract just quoted text and match it to chunks
                quote_match = re.search(r'["\']([^"\']{20,})["\']', line)
                if quote_match:
                    quote_text = quote_match.group(1).strip()
                    matching_chunk = self._find_best_matching_chunk(quote_text, chunks)
                    if matching_chunk:
                        highlights.append({
                            'quote': quote_text,
                            'timestamp': matching_chunk['timestamp'],
                            'start_time': matching_chunk['start_time'],
                        })
                        print(f"    ✓ Matched quote (no timestamp) to [{matching_chunk['timestamp']}]: {quote_text[:60]}...")
        
        print(f"    → Parsed {len(highlights)} total highlights from response")
        return highlights
    
    def _find_best_matching_chunk(self, quote: str, chunks: List[Dict]) -> Dict:
        """Find the chunk that best matches the quote using word overlap"""
        quote_words = set(quote.lower().split())
        best_chunk = None
        best_score = 0
        
        for chunk in chunks:
            chunk_words = set(chunk['text'].lower().split())
            # Calculate overlap score
            overlap = len(quote_words.intersection(chunk_words))
            score = overlap / len(quote_words) if quote_words else 0
            
            if score > best_score:
                best_score = score
                best_chunk = chunk
        
        # Return best match if score > 30%, otherwise first chunk
        if best_score > 0.3 and best_chunk:
            return best_chunk
        return chunks[0] if chunks else {'timestamp': '00:00', 'start_time': 0}
    
    def _find_timestamp_for_quote(self, quote: str, chunks: List[Dict]) -> Dict:
        """Find timestamp for a quote by searching in chunks"""
        # Normalize for comparison
        quote_lower = quote.lower()[:100]
        
        for chunk in chunks:
            chunk_text_lower = chunk['text'].lower()
            if quote_lower in chunk_text_lower:
                return {
                    'timestamp': chunk['timestamp'],
                    'start_time': chunk['start_time'],
                }
        
        # Default to first chunk if not found
        return {
            'timestamp': chunks[0]['timestamp'] if chunks else "00:00",
            'start_time': chunks[0]['start_time'] if chunks else 0,
        }
