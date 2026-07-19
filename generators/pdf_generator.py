"""
PDF Generator - 3 questions per page, compact and readable
"""

from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors

from config import OUTPUT_DIR, WORKBOOK_TITLE
from models.question import Question


class PDFGenerator:
    def __init__(self, questions: list[Question]) -> None:
        self.questions = questions
        self.output_file = OUTPUT_DIR / "SQL_Workbook.pdf"
        self.styles = None
    
    def generate(self) -> Path:
        doc = SimpleDocTemplate(
            str(self.output_file),
            pagesize=A4,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()
        
        story = []
        story.extend(self._create_title_page())
        story.append(PageBreak())
        story.extend(self._create_toc())
        story.append(PageBreak())
        
        # 3 questions per page
        for idx in range(0, len(self.questions), 3):
            for j in range(3):
                if idx + j < len(self.questions):
                    story.extend(self._create_question_block(self.questions[idx + j], idx + j + 1))
            story.append(PageBreak())
        
        doc.build(story)
        return self.output_file
    
    def _add_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='MainTitle', parent=self.styles['Title'],
            fontSize=24, textColor=colors.HexColor('#667eea'),
            alignment=TA_CENTER, spaceAfter=10, fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='SubTitle', parent=self.styles['Normal'],
            fontSize=14, textColor=colors.HexColor('#764ba2'),
            alignment=TA_CENTER, spaceAfter=15
        ))
        self.styles.add(ParagraphStyle(
            name='QNum', parent=self.styles['Normal'],
            fontSize=13, textColor=colors.HexColor('#2d3748'),
            spaceAfter=2, spaceBefore=4, fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='QText', parent=self.styles['Normal'],
            fontSize=12, textColor=colors.HexColor('#2d3748'),
            spaceAfter=2, spaceBefore=1, leading=15
        ))
        self.styles.add(ParagraphStyle(
            name='Hint', parent=self.styles['Normal'],
            fontSize=10, textColor=colors.HexColor('#667eea'),
            spaceAfter=6, leftIndent=6, fontName='Helvetica-Oblique'
        ))
        self.styles.add(ParagraphStyle(
            name='TOC', parent=self.styles['Heading1'],
            fontSize=18, textColor=colors.HexColor('#667eea'),
            alignment=TA_CENTER, spaceAfter=10
        ))
    
    def _create_title_page(self):
        story = []
        story.append(Paragraph("🐘 PostgreSQL Practice", self.styles['MainTitle']))
        story.append(Paragraph("SQL Mastery Workbook", self.styles['SubTitle']))
        
        diff_counts = {}
        for q in self.questions:
            diff_counts[q.difficulty] = diff_counts.get(q.difficulty, 0) + 1
        
        stats_data = [["Total", str(len(self.questions))]]
        for diff, count in diff_counts.items():
            stats_data.append([diff[:3], str(count)])
        
        stats_table = Table(stats_data, colWidths=[1*inch, 0.8*inch])
        stats_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f7fafc')),
            ('BACKGROUND', (1, 1), (1, -1), colors.HexColor('#edf2f7')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(
            datetime.now().strftime('%b %d, %Y'), self.styles['Normal']
        ))
        return story
    
    def _create_toc(self):
        story = []
        story.append(Paragraph("Contents", self.styles['TOC']))
        
        toc_data = []
        for i in range(0, len(self.questions), 3):
            row = []
            for j in range(3):
                if i+j < len(self.questions):
                    q = self.questions[i+j]
                    row.append(f"{i+j+1}. {q.topic[:15]}")
                else:
                    row.append("")
            toc_data.append(row)
        
        toc_table = Table(toc_data, colWidths=[1.8*inch, 1.8*inch, 1.8*inch])
        toc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(toc_table)
        return story
    
    def _create_question_block(self, question: Question, idx: int):
        story = []
        
        # Q1. SELECT (Beginner)
        story.append(Paragraph(
            f"Q{idx}. {question.topic} <font color='#764ba2'><i>({question.difficulty})</i></font>",
            self.styles['QNum']
        ))
        
        # Question text
        story.append(Paragraph(question.question, self.styles['QText']))
        
        # Answer lines (2 lines)
        story.append(Paragraph("_" * 55, self.styles['Normal']))
        story.append(Paragraph("_" * 55, self.styles['Normal']))
        
        # Hint
        story.append(Paragraph(f"💡 {question.tip}", self.styles['Hint']))
        
        return story
