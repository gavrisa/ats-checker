#!/usr/bin/env python3
"""
Create a test PDF with sufficient text content
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_test_pdf():
    """Create a PDF with enough text to pass preflight"""
    filename = "test_valid.pdf"
    
    # Create a new PDF
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Add text content
    text_content = """
    JANE DOE
    Senior UX/UI Designer
    
    EXPERIENCE
    Senior UX/UI Designer at Tech Company (2020-2024)
    - Led design of user interface for mobile applications
    - Conducted user research and usability testing
    - Collaborated with product managers and developers
    - Created wireframes, prototypes, and design systems
    
    UX Designer at Startup Inc. (2018-2020)
    - Designed user experiences for web applications
    - Worked with cross-functional teams
    - Implemented design thinking methodologies
    - Improved user engagement by 40%
    
    SKILLS
    - User Experience Design
    - User Interface Design
    - Prototyping
    - User Research
    - Figma
    - Adobe Creative Suite
    - HTML/CSS
    - JavaScript
    
    EDUCATION
    Bachelor of Design in Graphic Design
    University of Design (2014-2018)
    
    This resume contains sufficient text content to pass the preflight system
    and demonstrate the keyword matching functionality.
    """
    
    # Split text into lines and add to PDF
    lines = text_content.strip().split('\n')
    y_position = height - 50
    
    for line in lines:
        if line.strip():
            c.drawString(50, y_position, line.strip())
            y_position -= 20
        else:
            y_position -= 10
        
        # Check if we need a new page
        if y_position < 50:
            c.showPage()
            y_position = height - 50
    
    c.save()
    print(f"Created {filename} with {len(text_content)} characters")
    return filename

if __name__ == "__main__":
    create_test_pdf()

