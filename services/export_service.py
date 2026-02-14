"""
Export service for generating Markdown and PDF reports
"""
from typing import Dict, List
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import html


class ExportService:
    """Service for exporting summaries to Markdown and PDF"""
    
    def __init__(self):
        """Initialize export service"""
        self.styles = getSampleStyleSheet()
        self._setup_pdf_styles()
    
    def _escape_pdf_text(self, text: str) -> str:
        """
        Escape text for PDF rendering
        
        Args:
            text: Raw text
        
        Returns:
            Escaped text safe for PDF
        """
        if not text:
            return ""
        
        # Replace HTML entities and special characters
        text = html.escape(str(text))
        
        # Replace problematic characters
        replacements = {
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            '&#39;': "'",
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
            '\u2013': '-',  # En dash
            '\u2014': '-',  # Em dash
            '\u2026': '...',  # Ellipsis
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _setup_pdf_styles(self):
        """Setup custom PDF styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor='#1a1a1a',
            spaceAfter=30,
            alignment=TA_CENTER,
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor='#2c3e50',
            spaceAfter=12,
            spaceBefore=20,
        ))
        
        # Timestamp style
        self.styles.add(ParagraphStyle(
            name='Timestamp',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor='#7f8c8d',
            spaceAfter=6,
        ))
    
    def generate_markdown(self, summary_data: Dict) -> str:
        """
        Generate Markdown document from summary data
        
        Args:
            summary_data: Dictionary containing all summary information
        
        Returns:
            Markdown text
        """
        md_lines = []
        
        # Header
        md_lines.append(f"# {summary_data.get('title', 'Video Summary')}")
        md_lines.append("")
        md_lines.append(f"**Channel:** {summary_data.get('channel', 'Unknown')}")
        md_lines.append(f"**Video ID:** {summary_data.get('video_id', 'N/A')}")
        md_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # Executive Summary
        md_lines.append("## 📋 Executive Summary")
        md_lines.append("")
        executive_summary = summary_data.get('executive_summary', [])
        for i, bullet in enumerate(executive_summary, 1):
            md_lines.append(f"{i}. {bullet}")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # Section Summaries
        md_lines.append("## 📝 Section-by-Section Summary")
        md_lines.append("")
        section_summaries = summary_data.get('section_summaries', [])
        for i, section in enumerate(section_summaries, 1):
            timestamp = section.get('timestamp', '00:00')
            summary = section.get('summary', '')
            md_lines.append(f"### Section {i} [{timestamp}]")
            md_lines.append("")
            md_lines.append(summary)
            md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # Highlights
        md_lines.append("## ⭐ Key Highlights")
        md_lines.append("")
        highlights = summary_data.get('highlights', [])
        for i, highlight in enumerate(highlights, 1):
            quote = highlight.get('quote', '')
            timestamp = highlight.get('timestamp', '00:00')
            md_lines.append(f"{i}. **[{timestamp}]** \"{quote}\"")
            md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # Quality Metrics
        md_lines.append("## 📊 Quality Metrics")
        md_lines.append("")
        metrics = summary_data.get('metrics', {})
        md_lines.append(f"- **Coverage:** {metrics.get('coverage_percent', 0):.1f}%")
        md_lines.append(f"- **Confidence Score:** {metrics.get('confidence_score', 0):.2f}")
        md_lines.append(f"- **Total Chunks:** {metrics.get('total_chunks', 0)}")
        md_lines.append(f"- **Total Words:** {metrics.get('total_words', 0):,}")
        md_lines.append("")
        
        return "\n".join(md_lines)
    
    def save_markdown(self, summary_data: Dict, video_id: str, directory: str) -> str:
        """
        Save Markdown document to file
        
        Args:
            summary_data: Summary data dictionary
            video_id: YouTube video ID
            directory: Directory to save to
        
        Returns:
            File path
        """
        markdown_text = self.generate_markdown(summary_data)
        
        file_path = Path(directory) / f"{video_id}_summary.md"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)
        
        print(f"Markdown saved to {file_path}")
        return str(file_path)
    
    def generate_pdf(self, summary_data: Dict, output_path: str) -> str:
        """
        Generate PDF document from summary data
        
        Args:
            summary_data: Dictionary containing all summary information
            output_path: Path to save PDF
        
        Returns:
            File path
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Container for PDF elements
        story = []
        
        # Title
        title = self._escape_pdf_text(summary_data.get('title', 'Video Summary'))
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Metadata
        channel = self._escape_pdf_text(summary_data.get('channel', 'Unknown'))
        video_id = self._escape_pdf_text(summary_data.get('video_id', 'N/A'))
        metadata_text = f"""
        <b>Channel:</b> {channel}<br/>
        <b>Video ID:</b> {video_id}<br/>
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        story.append(Paragraph(metadata_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        executive_summary = summary_data.get('executive_summary', [])
        for i, bullet in enumerate(executive_summary, 1):
            bullet_text = self._escape_pdf_text(f"{i}. {bullet}")
            story.append(Paragraph(bullet_text, self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Section Summaries
        story.append(Paragraph("Section-by-Section Summary", self.styles['SectionHeader']))
        section_summaries = summary_data.get('section_summaries', [])
        
        for i, section in enumerate(section_summaries, 1):
            timestamp = self._escape_pdf_text(section.get('timestamp', '00:00'))
            summary = self._escape_pdf_text(section.get('summary', ''))
            
            # Section header with timestamp
            section_header = f"Section {i} [{timestamp}]"
            story.append(Paragraph(section_header, self.styles['Heading3']))
            
            # Summary text - wrap long text
            if len(summary) > 500:
                # Split long summaries into chunks
                chunks = [summary[i:i+500] for i in range(0, len(summary), 500)]
                for chunk in chunks:
                    story.append(Paragraph(chunk, self.styles['Normal']))
            else:
                story.append(Paragraph(summary, self.styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Highlights
        story.append(Paragraph("Key Highlights", self.styles['SectionHeader']))
        highlights = summary_data.get('highlights', [])
        
        for i, highlight in enumerate(highlights, 1):
            quote = self._escape_pdf_text(highlight.get('quote', ''))
            timestamp = self._escape_pdf_text(highlight.get('timestamp', '00:00'))
            
            highlight_text = f'{i}. [{timestamp}] "{quote}"'
            try:
                story.append(Paragraph(highlight_text, self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            except Exception as e:
                # If paragraph fails, add a simplified version
                simple_text = f'{i}. [{timestamp}] Quote available in markdown export'
                story.append(Paragraph(simple_text, self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
                print(f"Warning: Could not add highlight {i} to PDF: {e}")
        
        story.append(Spacer(1, 0.3*inch))
        
        # Quality Metrics
        story.append(Paragraph("Quality Metrics", self.styles['SectionHeader']))
        metrics = summary_data.get('metrics', {})
        
        metrics_text = f"""
        Coverage: {metrics.get('coverage_percent', 0):.1f}%<br/>
        Confidence Score: {metrics.get('confidence_score', 0):.2f}<br/>
        Total Chunks: {metrics.get('total_chunks', 0)}<br/>
        Total Words: {metrics.get('total_words', 0):,}
        """
        story.append(Paragraph(metrics_text, self.styles['Normal']))
        
        # Build PDF with error handling
        try:
            doc.build(story)
            print(f"✓ PDF saved to {output_path}")
        except Exception as e:
            print(f"✗ Error building PDF: {type(e).__name__}: {e}")
            # Try to build with minimal content
            try:
                minimal_story = [
                    Paragraph(self._escape_pdf_text(summary_data.get('title', 'Video Summary')), 
                             self.styles['CustomTitle']),
                    Spacer(1, 0.3*inch),
                    Paragraph("An error occurred generating the full PDF. Please use Markdown export.", 
                             self.styles['Normal'])
                ]
                doc.build(minimal_story)
                print(f"✓ Minimal PDF created at {output_path}")
            except Exception as e2:
                print(f"✗ Failed to create minimal PDF: {e2}")
                raise e
        
        return output_path
    
    def save_pdf(self, summary_data: Dict, video_id: str, directory: str) -> str:
        """
        Save PDF document to file
        
        Args:
            summary_data: Summary data dictionary
            video_id: YouTube video ID
            directory: Directory to save to
        
        Returns:
            File path
        """
        file_path = Path(directory) / f"{video_id}_summary.pdf"
        return self.generate_pdf(summary_data, str(file_path))
