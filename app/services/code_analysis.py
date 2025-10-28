"""
LangChain-powered AI Code Analysis Service
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from typing import List, Dict, Any, Optional
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class CodeAnalysisService:
    """AI-powered code analysis using LangChain"""
    
    def __init__(self):
        """Initialize the code analysis service"""
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_MODEL,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            openai_api_key=settings.OPENAI_API_KEY
        )
        self.memory = ConversationBufferMemory()
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Setup LangChain prompts for different analysis types"""
        
        # System prompt for code analysis
        self.system_prompt = """You are an expert code reviewer and software engineer with deep knowledge of:
- Security vulnerabilities and best practices
- Performance optimization techniques
- Code quality and maintainability
- Bug patterns and edge cases
- Modern software development practices

Analyze the provided code and identify:
1. Security vulnerabilities
2. Performance issues
3. Code quality problems
4. Potential bugs
5. Improvement suggestions

Provide specific, actionable feedback with code examples when possible."""

        # Bug detection prompt
        self.bug_detection_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content="""
Analyze this code for potential bugs and issues:

File: {file_path}
Language: {language}
Code:
```{language}
{code}
```

Context:
- Repository: {repository_name}
- Pull Request: {pr_title}
- Changed lines: {changed_lines}

Focus on:
- Logic errors
- Edge cases
- Null pointer exceptions
- Array bounds issues
- Race conditions
- Memory leaks

Return your analysis in JSON format:
{{
    "bugs": [
        {{
            "line": 42,
            "type": "null_pointer",
            "severity": "high",
            "title": "Potential null pointer exception",
            "description": "Variable 'user' could be null when accessing 'user.name'",
            "suggestion": "Add null check: if (user != null) {{ return user.name; }}"
        }}
    ],
    "confidence": 85
}}
""")
        ])
        
        # Security analysis prompt
        self.security_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content="""
Analyze this code for security vulnerabilities:

File: {file_path}
Language: {language}
Code:
```{language}
{code}
```

Context:
- Repository: {repository_name}
- Pull Request: {pr_title}
- Changed lines: {changed_lines}

Focus on:
- SQL injection
- XSS vulnerabilities
- Authentication bypass
- Authorization issues
- Input validation
- Secret exposure
- Insecure dependencies

Return your analysis in JSON format:
{{
    "security_issues": [
        {{
            "line": 15,
            "type": "sql_injection",
            "severity": "critical",
            "title": "SQL Injection vulnerability",
            "description": "User input directly concatenated into SQL query",
            "suggestion": "Use parameterized queries or prepared statements"
        }}
    ],
    "confidence": 95
}}
""")
        ])
        
        # Code quality prompt
        self.quality_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            HumanMessage(content="""
Analyze this code for quality and maintainability issues:

File: {file_path}
Language: {language}
Code:
```{language}
{code}
```

Context:
- Repository: {repository_name}
- Pull Request: {pr_title}
- Changed lines: {changed_lines}

Focus on:
- Code complexity
- Naming conventions
- Code duplication
- Error handling
- Documentation
- Test coverage
- Design patterns

Return your analysis in JSON format:
{{
    "quality_issues": [
        {{
            "line": 30,
            "type": "complexity",
            "severity": "medium",
            "title": "High cyclomatic complexity",
            "description": "Function has too many conditional branches",
            "suggestion": "Consider breaking into smaller functions"
        }}
    ],
    "confidence": 75
}}
""")
        ])
    
    async def analyze_code(self, 
                          code: str, 
                          file_path: str, 
                          language: str,
                          repository_name: str,
                          pr_title: str,
                          changed_lines: List[int]) -> Dict[str, Any]:
        """Analyze code for bugs, security issues, and quality problems"""
        
        try:
            logger.info(f"Analyzing code in {file_path}")
            
            # Prepare context
            context = {
                "file_path": file_path,
                "language": language,
                "code": code,
                "repository_name": repository_name,
                "pr_title": pr_title,
                "changed_lines": changed_lines
            }
            
            # Run different analysis types
            bug_analysis = await self._run_analysis(self.bug_detection_prompt, context)
            security_analysis = await self._run_analysis(self.security_prompt, context)
            quality_analysis = await self._run_analysis(self.quality_prompt, context)
            
            # Combine results
            results = {
                "file_path": file_path,
                "language": language,
                "bugs": bug_analysis.get("bugs", []),
                "security_issues": security_analysis.get("security_issues", []),
                "quality_issues": quality_analysis.get("quality_issues", []),
                "overall_confidence": self._calculate_overall_confidence([
                    bug_analysis.get("confidence", 0),
                    security_analysis.get("confidence", 0),
                    quality_analysis.get("confidence", 0)
                ])
            }
            
            logger.info(f"Analysis completed for {file_path}")
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing code in {file_path}: {str(e)}")
            return {
                "file_path": file_path,
                "language": language,
                "bugs": [],
                "security_issues": [],
                "quality_issues": [],
                "error": str(e)
            }
    
    async def _run_analysis(self, prompt: ChatPromptTemplate, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run a specific analysis using LangChain"""
        try:
            # Create chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Run analysis
            response = await chain.arun(**context)
            
            # Parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, returning raw text")
                return {"raw_response": response, "confidence": 50}
                
        except Exception as e:
            logger.error(f"Error in analysis: {str(e)}")
            return {"error": str(e), "confidence": 0}
    
    def _calculate_overall_confidence(self, confidences: List[int]) -> int:
        """Calculate overall confidence from individual analysis confidences"""
        if not confidences:
            return 0
        return sum(confidences) // len(confidences)
    
    async def generate_review_summary(self, 
                                    repository_name: str,
                                    pr_title: str,
                                    analysis_results: List[Dict[str, Any]]) -> str:
        """Generate a summary of the code review"""
        
        try:
            # Count issues by type
            total_bugs = sum(len(result.get("bugs", [])) for result in analysis_results)
            total_security = sum(len(result.get("security_issues", [])) for result in analysis_results)
            total_quality = sum(len(result.get("quality_issues", [])) for result in analysis_results)
            
            summary_prompt = f"""
Generate a concise code review summary for:

Repository: {repository_name}
Pull Request: {pr_title}

Analysis Results:
- Files analyzed: {len(analysis_results)}
- Bugs found: {total_bugs}
- Security issues: {total_security}
- Quality issues: {total_quality}

Provide a professional summary highlighting:
1. Overall assessment
2. Critical issues that need immediate attention
3. Recommendations for improvement
4. Positive aspects (if any)

Keep it concise and actionable.
"""
            
            messages = [
                SystemMessage(content="You are an expert code reviewer providing professional feedback."),
                HumanMessage(content=summary_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating review summary: {str(e)}")
            return f"Code review completed. Found {total_bugs} bugs, {total_security} security issues, and {total_quality} quality issues."
