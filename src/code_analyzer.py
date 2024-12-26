from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass
import streamlit as st

@dataclass
class CodeAnalysis:
    """Store code analysis results"""
    metrics: Dict[str, Any]
    suggestions: List[str]
    warnings: List[str]
    score: float = 0.0

@dataclass
class AnalysisResult:
    """Complete analysis results"""
    html: CodeAnalysis
    css: CodeAnalysis
    js: CodeAnalysis
    overall_score: float = 0.0

class CodeAnalyzer:
    """Analyze and optimize code"""
    
    def analyze_all(self, html: str, css: str, js: str) -> AnalysisResult:
        """Analyze all code components"""
        html_analysis = self.analyze_html(html)
        css_analysis = self.analyze_css(css)
        js_analysis = self.analyze_js(js)
        
        # Calculate overall score
        overall_score = (html_analysis.score + css_analysis.score + js_analysis.score) / 3
        
        return AnalysisResult(
            html=html_analysis,
            css=css_analysis,
            js=js_analysis,
            overall_score=overall_score
        )

    def analyze_html(self, html: str) -> CodeAnalysis:
        """Analyze HTML structure and accessibility"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            metrics = {
                "elements": len(soup.find_all()),
                "headings": len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
                "images": len(soup.find_all('img')),
                "links": len(soup.find_all('a')),
                "forms": len(soup.find_all('form')),
                "buttons": len(soup.find_all('button')),
                "semantic_elements": len(soup.find_all([
                    'header', 'nav', 'main', 'article', 'section', 'aside', 'footer'
                ])),
                "interactive_elements": len(soup.find_all(['button', 'a', 'input', 'select', 'textarea'])),
                "text_content": len(soup.get_text().split())
            }
            
            warnings = []
            suggestions = []
            score = 100.0
            
            # Check for accessibility issues
            images_without_alt = soup.find_all('img', alt=False)
            if images_without_alt:
                warnings.append(f"Found {len(images_without_alt)} images without alt text")
                score -= 10
                suggestions.append("Add alt text to all images for better accessibility")

            # Check heading hierarchy
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if headings and not soup.find('h1'):
                warnings.append("No h1 heading found")
                score -= 5
                suggestions.append("Add an h1 heading as the main title")

            # Check for semantic structure
            if not soup.find(['header', 'main', 'footer']):
                suggestions.append("Consider using semantic elements (header, main, footer)")
                score -= 5

            # Check for form labels
            forms = soup.find_all('form')
            for form in forms:
                inputs = form.find_all(['input', 'select', 'textarea'])
                labels = form.find_all('label')
                if len(inputs) > len(labels):
                    warnings.append(f"Form has {len(inputs)} inputs but only {len(labels)} labels")
                    score -= 5
                    suggestions.append("Add labels for all form inputs")

            return CodeAnalysis(metrics, suggestions, warnings, max(0, score))
            
        except Exception as e:
            st.error(f"Error analyzing HTML: {str(e)}")
            return CodeAnalysis({}, [], [f"Analysis error: {str(e)}"], 0)

    def analyze_css(self, css: str) -> CodeAnalysis:
        """Analyze CSS complexity and best practices"""
        try:
            metrics = {
                "selectors": len(re.findall(r'[^}]+{', css)),
                "properties": len(re.findall(r'[^:]+:', css)),
                "media_queries": len(re.findall(r'@media', css)),
                "colors": len(set(re.findall(r'#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)', css))),
                "file_size": len(css.encode('utf-8')),
                "important_rules": len(re.findall(r'!important', css)),
                "vendor_prefixes": len(re.findall(r'-webkit-|-moz-|-ms-|-o-', css)),
                "custom_properties": len(re.findall(r'--[^:]+:', css))
            }
            
            warnings = []
            suggestions = []
            score = 100.0
            
            # Check for potential issues
            if metrics["important_rules"] > 0:
                warnings.append(f"Found {metrics['important_rules']} !important declarations")
                score -= metrics["important_rules"] * 2
                suggestions.append("Avoid using !important declarations")

            if metrics["vendor_prefixes"] > 0:
                suggestions.append("Consider using a CSS preprocessor or autoprefixer")

            if metrics["selectors"] > 50:
                warnings.append("Large number of selectors may impact performance")
                score -= 5
                suggestions.append("Consider refactoring and combining selectors")

            if not metrics["media_queries"]:
                suggestions.append("Add media queries for responsive design")
                score -= 5

            if not metrics["custom_properties"]:
                suggestions.append("Consider using CSS custom properties for better maintainability")

            return CodeAnalysis(metrics, suggestions, warnings, max(0, score))
            
        except Exception as e:
            st.error(f"Error analyzing CSS: {str(e)}")
            return CodeAnalysis({}, [], [f"Analysis error: {str(e)}"], 0)

    def analyze_js(self, js: str) -> CodeAnalysis:
        """Analyze JavaScript complexity and patterns"""
        try:
            metrics = {
                "file_size": len(js.encode('utf-8')),
                "functions": len(re.findall(r'function\s+\w+\s*\(|const\s+\w+\s*=\s*\([^)]*\)\s*=>', js)),
                "variables": len(re.findall(r'var\s+\w+|let\s+\w+|const\s+\w+', js)),
                "event_listeners": len(re.findall(r'addEventListener', js)),
                "dom_queries": len(re.findall(r'querySelector|getElementById|getElementsBy', js)),
                "loops": len(re.findall(r'for\s*\(|while\s*\(', js)),
                "conditionals": len(re.findall(r'if\s*\(|switch\s*\(', js)),
                "async_operations": len(re.findall(r'async|await|Promise|fetch|setTimeout', js))
            }
            
            warnings = []
            suggestions = []
            score = 100.0
            
            # Check for potential issues
            if re.search(r'var\s+\w+', js):
                warnings.append("Found usage of 'var' keyword")
                score -= 5
                suggestions.append("Use 'const' or 'let' instead of 'var'")

            if metrics["dom_queries"] > 5:
                suggestions.append("Consider caching DOM queries for better performance")
                score -= 3

            if not re.search(r'=>|async|await', js):
                suggestions.append("Consider using modern JS features (arrow functions, async/await)")
                score -= 5

            if metrics["event_listeners"] > 10:
                warnings.append("Large number of event listeners may impact performance")
                score -= 5
                suggestions.append("Consider event delegation for multiple similar events")

            if not re.search(r'try\s*{', js) and metrics["async_operations"] > 0:
                suggestions.append("Add error handling for async operations")
                score -= 3

            return CodeAnalysis(metrics, suggestions, warnings, max(0, score))
            
        except Exception as e:
            st.error(f"Error analyzing JavaScript: {str(e)}")
            return CodeAnalysis({}, [], [f"Analysis error: {str(e)}"], 0)

    def display_analysis(self, result: AnalysisResult) -> None:
        """Display analysis results in Streamlit"""
        st.header("Code Analysis")
        
        # Overall score
        st.metric("Overall Score", f"{result.overall_score:.1f}%")
        
        # Individual analyses
        tabs = st.tabs(["HTML", "CSS", "JavaScript"])
        
        with tabs[0]:
            self._display_component_analysis("HTML", result.html)
            
        with tabs[1]:
            self._display_component_analysis("CSS", result.css)
            
        with tabs[2]:
            self._display_component_analysis("JavaScript", result.js)

    def _display_component_analysis(self, title: str, analysis: CodeAnalysis) -> None:
        """Display individual component analysis"""
        st.subheader(f"{title} Analysis")
        st.metric(f"{title} Score", f"{analysis.score:.1f}%")
        
        # Metrics
        st.write("Metrics:")
        for key, value in analysis.metrics.items():
            st.text(f"{key.replace('_', ' ').title()}: {value}")
        
        # Warnings
        if analysis.warnings:
            st.warning("Warnings:")
            for warning in analysis.warnings:
                st.write(f"- {warning}")
        
        # Suggestions
        if analysis.suggestions:
            st.info("Suggestions:")
            for suggestion in analysis.suggestions:
                st.write(f"- {suggestion}")