"""
Performance tests for the ATS checker
"""
import pytest
import time
import sys
import os

# Add the parent directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import extract_ats_keywords, match_keywords_to_cv

class TestPerformance:
    """Test performance characteristics"""
    
    def test_keyword_extraction_performance_small(self):
        """Test performance with small text"""
        text = "User experience designer with research skills" * 10
        
        start_time = time.time()
        keywords = extract_ats_keywords(text)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 1.0  # Should complete in under 1 second
        assert isinstance(keywords, list)
    
    def test_keyword_extraction_performance_medium(self):
        """Test performance with medium text"""
        text = """
        Senior UX Designer position requiring extensive user research experience.
        Candidate must have skills in wireframing, prototyping, and usability testing.
        Experience with accessibility standards and design systems is required.
        Knowledge of qualitative and quantitative research methods is essential.
        Must be able to work with cross-functional teams and stakeholders.
        """ * 50  # Repeat 50 times
        
        start_time = time.time()
        keywords = extract_ats_keywords(text)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 5.0  # Should complete in under 5 seconds
        assert len(keywords) <= 30  # Should respect limits
    
    def test_keyword_extraction_performance_large(self):
        """Test performance with large text"""
        # Create a large job description
        base_text = """
        Senior UX Designer position requiring extensive user research experience.
        Candidate must have skills in wireframing, prototyping, and usability testing.
        Experience with accessibility standards and design systems is required.
        Knowledge of qualitative and quantitative research methods is essential.
        Must be able to work with cross-functional teams and stakeholders.
        Should have experience with information architecture and interaction design.
        Portfolio should demonstrate user-centered design processes and outcomes.
        Experience with design tools like Figma, Sketch, and Adobe Creative Suite.
        """
        large_text = base_text * 200  # Very large text
        
        start_time = time.time()
        keywords = extract_ats_keywords(large_text)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 30.0  # Should complete in under 30 seconds (timeout limit)
        assert len(keywords) <= 30  # Should respect limits
    
    def test_keyword_matching_performance(self):
        """Test performance of keyword matching"""
        jd_keywords = ["user research", "wireframing", "accessibility", "design systems"] * 25  # 100 keywords
        cv_text = """
        Experienced UX designer with strong background in user research and usability testing.
        Skilled in wireframing, prototyping, and creating accessible design solutions.
        Experience with design systems and component libraries.
        """ * 100  # Large CV text
        
        start_time = time.time()
        result = match_keywords_to_cv(jd_keywords, cv_text)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 2.0  # Should complete in under 2 seconds
        assert "matched_keywords" in result
        assert "missing_keywords" in result
    
    def test_timeout_handling(self):
        """Test that the system handles timeouts gracefully"""
        # Create an extremely repetitive text that might cause performance issues
        problematic_text = "user experience design research wireframing prototyping accessibility " * 1000
        
        # The function should handle this gracefully and not hang
        start_time = time.time()
        keywords = extract_ats_keywords(problematic_text)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 35.0  # Should not exceed timeout significantly
        assert isinstance(keywords, list)  # Should still return a result
    
    def test_memory_usage_large_input(self):
        """Test that memory usage remains reasonable with large inputs"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process large text
        large_text = "user experience design research accessibility " * 5000
        keywords = extract_ats_keywords(large_text)
        
        # Get final memory usage
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for this test)
        assert memory_increase < 100
        assert isinstance(keywords, list)

class TestScalability:
    """Test scalability characteristics"""
    
    def test_concurrent_processing_simulation(self):
        """Simulate concurrent processing by running multiple extractions"""
        text = "UX Designer with user research and accessibility experience"
        
        start_time = time.time()
        
        # Simulate 10 concurrent requests
        results = []
        for i in range(10):
            keywords = extract_ats_keywords(text)
            results.append(keywords)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete all 10 in reasonable time
        assert execution_time < 10.0
        assert len(results) == 10
        assert all(isinstance(result, list) for result in results)
    
    def test_repeated_calls_performance(self):
        """Test performance degrades gracefully with repeated calls"""
        text = "Senior UX Designer with extensive research experience"
        
        times = []
        for i in range(5):
            start_time = time.time()
            keywords = extract_ats_keywords(text)
            end_time = time.time()
            times.append(end_time - start_time)
        
        # Performance should be consistent across calls
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # Max time should not be significantly higher than average
        assert max_time < avg_time * 3  # No more than 3x slower than average
        assert all(t < 2.0 for t in times)  # All calls should be under 2 seconds
