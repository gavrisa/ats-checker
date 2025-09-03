"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

@pytest.fixture
def sample_jd():
    """Sample job description for testing"""
    return """
    Senior UX Designer
    
    We are looking for a Senior UX Designer to join our product development team. You will be responsible for creating user-centered design solutions that enhance the user experience across our SaaS platform.
    
    Key Responsibilities:
    - Conduct user research and usability testing to understand user needs and pain points
    - Create wireframes, interactive prototypes, and user journeys to communicate design concepts
    - Develop personas and experience maps to guide design decisions
    - Collaborate with product development teams to implement design solutions
    - Ensure accessibility compliance (WCAG) across all design deliverables
    - Conduct qualitative and quantitative research to validate design decisions
    - Create design systems and information architecture for scalable solutions
    - Perform heuristics evaluation and A/B testing to optimize user experience
    - Lead stakeholder alignment sessions to gather requirements and feedback
    - Implement mixed-methods research approaches for comprehensive insights
    """

@pytest.fixture
def sample_cv():
    """Sample CV for testing"""
    return """
    JOHN DOE
    UX Designer & Researcher
    
    EXPERIENCE
    
    Senior UX Designer | TechCorp | 2020-2023
    - Led user research initiatives using qualitative and quantitative methods
    - Created wireframes and interactive prototypes for mobile applications
    - Developed user personas and journey maps for e-commerce platform
    - Conducted usability testing sessions with 50+ participants
    - Implemented accessibility improvements achieving WCAG 2.1 AA compliance
    - Collaborated with product teams to deliver user-centered solutions
    - Created design systems and component libraries for consistency
    
    SKILLS
    - User Research & Usability Testing
    - Wireframing & Prototyping
    - Design Systems & Information Architecture
    - Accessibility (WCAG) Compliance
    - Figma, Sketch, Adobe Creative Suite
    - Qualitative & Quantitative Research Methods
    - Stakeholder Management & Collaboration
    - A/B Testing & Analytics
    """

@pytest.fixture
def empty_text():
    """Empty text for testing"""
    return ""

@pytest.fixture
def long_text():
    """Very long text for testing limits"""
    return "word " * 20000  # 20,000 words
