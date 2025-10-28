"""
Static Analysis Service
"""

import subprocess
import json
import logging
import tempfile
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class StaticAnalysisService:
    """Service for static code analysis using various tools"""
    
    def __init__(self):
        """Initialize static analysis service"""
        self.tools = {
            "bandit": self._run_bandit,
            "safety": self._run_safety,
            "semgrep": self._run_semgrep
        }
    
    async def analyze_code(self, code: str, language: str, file_path: str) -> Dict[str, Any]:
        """Run static analysis on code"""
        results = {
            "file_path": file_path,
            "language": language,
            "security_issues": [],
            "quality_issues": [],
            "dependency_issues": []
        }
        
        try:
            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(mode='w', suffix=self._get_file_extension(language), delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            try:
                # Run different analysis tools based on language
                if language.lower() in ['python', 'py']:
                    security_results = await self._run_bandit(temp_file_path)
                    results["security_issues"].extend(security_results)
                    
                    dependency_results = await self._run_safety(temp_file_path)
                    results["dependency_issues"].extend(dependency_results)
                
                # Run Semgrep for multiple languages
                semgrep_results = await self._run_semgrep(temp_file_path, language)
                results["security_issues"].extend(semgrep_results.get("security", []))
                results["quality_issues"].extend(semgrep_results.get("quality", []))
                
            finally:
                # Clean up temporary file
                os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Error in static analysis for {file_path}: {str(e)}")
            results["error"] = str(e)
        
        return results
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c',
            'go': '.go',
            'rust': '.rs'
        }
        return extensions.get(language.lower(), '.txt')
    
    async def _run_bandit(self, file_path: str) -> List[Dict[str, Any]]:
        """Run Bandit security analysis"""
        try:
            result = subprocess.run([
                'bandit', '-f', 'json', file_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                issues = []
                for result_item in data.get('results', []):
                    issues.append({
                        "line": result_item.get('line_number'),
                        "type": "security",
                        "severity": result_item.get('issue_severity', 'medium'),
                        "title": result_item.get('issue_text', 'Security issue'),
                        "description": result_item.get('issue_description', ''),
                        "tool": "bandit",
                        "confidence": 80
                    })
                return issues
            else:
                logger.warning(f"Bandit analysis failed: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            logger.warning("Bandit analysis timed out")
            return []
        except Exception as e:
            logger.error(f"Error running Bandit: {str(e)}")
            return []
    
    async def _run_safety(self, file_path: str) -> List[Dict[str, Any]]:
        """Run Safety dependency analysis"""
        try:
            # Safety analyzes requirements files, not individual Python files
            # This is a placeholder for when we have requirements.txt
            return []
            
        except Exception as e:
            logger.error(f"Error running Safety: {str(e)}")
            return []
    
    async def _run_semgrep(self, file_path: str, language: str) -> Dict[str, List[Dict[str, Any]]]:
        """Run Semgrep analysis"""
        try:
            # Map language names to Semgrep language identifiers
            lang_map = {
                'python': 'python',
                'javascript': 'javascript',
                'typescript': 'typescript',
                'java': 'java',
                'cpp': 'cpp',
                'c': 'c',
                'go': 'go',
                'rust': 'rust'
            }
            
            semgrep_lang = lang_map.get(language.lower())
            if not semgrep_lang:
                return {"security": [], "quality": []}
            
            result = subprocess.run([
                'semgrep', '--config=auto', '--json', '--lang', semgrep_lang, file_path
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                security_issues = []
                quality_issues = []
                
                for result_item in data.get('results', []):
                    issue = {
                        "line": result_item.get('start', {}).get('line'),
                        "type": result_item.get('extra', {}).get('metadata', {}).get('category', 'unknown'),
                        "severity": result_item.get('extra', {}).get('severity', 'medium'),
                        "title": result_item.get('extra', {}).get('message', 'Issue found'),
                        "description": result_item.get('extra', {}).get('message', ''),
                        "tool": "semgrep",
                        "confidence": 85
                    }
                    
                    # Categorize issues
                    if issue["type"] in ['security', 'vulnerability']:
                        security_issues.append(issue)
                    else:
                        quality_issues.append(issue)
                
                return {
                    "security": security_issues,
                    "quality": quality_issues
                }
            else:
                logger.warning(f"Semgrep analysis failed: {result.stderr}")
                return {"security": [], "quality": []}
                
        except subprocess.TimeoutExpired:
            logger.warning("Semgrep analysis timed out")
            return {"security": [], "quality": []}
        except Exception as e:
            logger.error(f"Error running Semgrep: {str(e)}")
            return {"security": [], "quality": []}
    
    async def analyze_dependencies(self, requirements_file: str) -> List[Dict[str, Any]]:
        """Analyze dependencies for vulnerabilities"""
        try:
            result = subprocess.run([
                'safety', 'check', '--json', '--file', requirements_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:  # Safety returns non-zero for vulnerabilities found
                data = json.loads(result.stdout)
                issues = []
                for item in data:
                    issues.append({
                        "package": item.get('package_name'),
                        "version": item.get('installed_version'),
                        "vulnerability": item.get('advisory'),
                        "severity": "high",
                        "title": f"Vulnerability in {item.get('package_name')}",
                        "description": item.get('advisory'),
                        "tool": "safety",
                        "confidence": 95
                    })
                return issues
            return []
            
        except Exception as e:
            logger.error(f"Error analyzing dependencies: {str(e)}")
            return []
