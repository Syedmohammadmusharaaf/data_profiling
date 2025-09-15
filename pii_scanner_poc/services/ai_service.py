"""
AI Service Layer for PII Scanner
Handles all interactions with AI models including Azure OpenAI
"""

import time
import json
import re
from typing import Optional, Dict, Any, List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage

from pii_scanner_poc.models.data_models import (
    AIModelResponse, BatchAnalysisRequest, JSONExtractionAttempt,
    RiskLevel, PIIType, Regulation
)
from pii_scanner_poc.config.config_manager import config_manager
from pii_scanner_poc.utils.logging_config import ai_logger, log_function_entry, log_function_exit, log_performance


class AIService:
    """Service for interacting with AI models"""
    
    def __init__(self):
        self.config = config_manager.get_config().ai_config
        self.llm = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Azure OpenAI client"""
        try:
            log_function_entry(ai_logger, "_initialize_client")
            
            self.llm = AzureChatOpenAI(
                azure_endpoint=self.config.endpoint,
                api_key=self.config.api_key,
                api_version=self.config.api_version,
                azure_deployment=self.config.deployment_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                timeout=self.config.timeout
            )
            
            ai_logger.info("AI client initialized successfully", extra={
                'component': 'ai_service',
                'endpoint': self.config.endpoint,
                'deployment': self.config.deployment_name,
                'temperature': self.config.temperature,
                'max_tokens': self.config.max_tokens
            })
            
            log_function_exit(ai_logger, "_initialize_client", "Client initialized")
            
        except Exception as e:
            ai_logger.error("Failed to initialize AI client", extra={
                'component': 'ai_service',
                'error': str(e)
            })
            raise
    
    def generate_batch_analysis_prompt(self, request: BatchAnalysisRequest) -> str:
        """Generate a comprehensive prompt for batch analysis"""
        log_function_entry(ai_logger, "generate_batch_analysis_prompt", 
                          tables=len(request.tables), 
                          total_columns=request.total_columns)
        
        try:
            # Build regulation-specific guidance
            regulation_guidance = self._build_regulation_guidance(request.regulations)
            
            # Format all tables and columns
            tables_text = self._format_tables_for_prompt(request.tables)
            
            # Create the comprehensive prompt
            prompt = self._create_prompt_template(
                request=request,
                regulation_guidance=regulation_guidance,
                tables_text=tables_text
            )
            
            ai_logger.info("Batch analysis prompt generated", extra={
                'component': 'ai_service',
                'prompt_length': len(prompt),
                'batch_number': request.batch_number,
                'tables': len(request.tables),
                'columns': request.total_columns
            })
            
            log_function_exit(ai_logger, "generate_batch_analysis_prompt", 
                            f"Prompt generated: {len(prompt)} characters")
            
            return prompt
            
        except Exception as e:
            ai_logger.error("Failed to generate batch analysis prompt", extra={
                'component': 'ai_service',
                'batch_number': request.batch_number,
                'error': str(e)
            })
            raise
    
    def _build_regulation_guidance(self, regulations: List[Regulation]) -> str:
        """Build regulation-specific guidance text"""
        guidance = ""
        
        if Regulation.GDPR in regulations:
            guidance += """
**GDPR (General Data Protection Regulation):**
- Personal identifiers: names, email addresses, phone numbers, addresses
- Online identifiers: IP addresses, device IDs, user IDs, cookies
- Special categories: health data, biometric data, genetic data, racial/ethnic origin
- Location data and behavioral tracking information
- Employment and educational records
"""
        
        if Regulation.HIPAA in regulations:
            guidance += """
**HIPAA (Health Insurance Portability and Accountability Act):**
- Direct identifiers: names, addresses, dates (except year), phone/fax numbers
- Medical identifiers: medical record numbers, health plan beneficiary numbers
- Account and license numbers related to healthcare
- Health information, medical conditions, treatment data
- Biometric identifiers, photographs, and voice recordings
"""
        
        if Regulation.CCPA in regulations:
            guidance += """
**CCPA (California Consumer Privacy Act):**
- Personal information that identifies or relates to a consumer/household
- Commercial information and purchasing records
- Internet activity and browsing history
- Geolocation data and audio/visual recordings
- Professional and employment information
"""
        
        return guidance
    
    def _format_tables_for_prompt(self, tables: Dict[str, List[Any]]) -> str:
        """Format tables and columns for the prompt"""
        tables_text = ""
        
        for table_name, columns in tables.items():
            column_list = []
            for col in columns:
                if hasattr(col, 'column_name') and hasattr(col, 'data_type'):
                    column_list.append(f"  - {col.column_name} ({col.data_type})")
                else:
                    # Fallback for dict-like objects
                    column_list.append(f"  - {col.get('column_name', 'unknown')} ({col.get('data_type', 'unknown')})")
            
            tables_text += f"""
**Table: {table_name}**
{chr(10).join(column_list)}
"""
        
        return tables_text
    
    def _create_prompt_template(self, request: BatchAnalysisRequest, 
                               regulation_guidance: str, tables_text: str) -> str:
        """Create the complete prompt template"""
        regulation_names = [reg.value for reg in request.regulations]
        
        return f"""You are an expert data privacy and compliance analyst. Analyze the following {len(request.tables)} database tables for sensitive data according to {', '.join(regulation_names)} regulations.

**CRITICAL INSTRUCTIONS:**
1. Count sensitive columns EXACTLY - ensure your count matches the actual sensitive fields you identify
2. Analyze ONLY for {', '.join(regulation_names)} regulations
3. Be precise and consistent in your analysis
4. Return ONLY valid JSON with no additional text or formatting
5. Do NOT use markdown code blocks (```json)
6. Do NOT include explanations or additional text
7. Ensure proper JSON formatting with correct commas and brackets

**Tables to Analyze:**
{tables_text}

**Regulatory Scope:**
{regulation_guidance.strip()}

**Classification Criteria:**
- **High Risk:** Direct identifiers that can immediately identify individuals
- **Medium Risk:** Quasi-identifiers that could identify individuals when combined
- **Low Risk:** General tracking data with limited identification potential

**REQUIRED JSON OUTPUT FORMAT:**
{{
  "batch_analysis": {{
    "total_tables": {len(request.tables)},
    "total_columns": {request.total_columns},
    "regulations_checked": {regulation_names},
    "analysis_timestamp": "{time.strftime('%Y-%m-%d %H:%M:%S')}"
  }},
  "table_results": [
    {{
      "table_name": "table_name",
      "risk_level": "High|Medium|Low",
      "total_columns": number,
      "sensitive_columns": number,
      "applicable_regulations": {regulation_names},
      "column_analysis": [
        {{
          "column_name": "column_name",
          "data_type": "data_type",
          "is_sensitive": true|false,
          "sensitivity_level": "High|Medium|Low|None",
          "pii_type": "Name|Email|Phone|Address|ID|Medical|Financial|Network|Other|None",
          "applicable_regulations": ["regulation1", "regulation2"],
          "risk_explanation": "Brief explanation why this field is/isn't sensitive"
        }}
      ]
    }}
  ]
}}

**VALIDATION REQUIREMENTS:**
- Ensure "sensitive_columns" count exactly matches the number of columns marked "is_sensitive": true
- Include ALL columns in column_analysis, even non-sensitive ones
- Use consistent regulation names: {regulation_names}
- Provide clear, factual risk explanations

**CRITICAL OUTPUT INSTRUCTIONS:**
- Return ONLY valid JSON - no text before or after
- Do NOT use markdown code blocks (```json)
- Do NOT include explanations or additional text
- Ensure proper JSON formatting with correct commas and brackets
- Test your JSON is valid before responding

Analyze now and return ONLY the JSON response:"""
    
    def send_analysis_request(self, prompt: str, batch_number: int, timeout_override: Optional[int] = None) -> AIModelResponse:
        """Send analysis request to AI model and get response"""
        log_function_entry(ai_logger, "send_analysis_request", 
                          prompt_length=len(prompt), 
                          batch_number=batch_number)
        
        start_time = time.time()
        timeout = timeout_override or self.config.timeout
        
        try:
            ai_logger.info("Sending request to AI model", extra={
                'component': 'ai_service',
                'batch_number': batch_number,
                'prompt_length': len(prompt),
                'model': self.config.deployment_name,
                'timeout': timeout
            })
            
            # Create a temporary LLM instance with specific timeout if needed
            if timeout_override and timeout_override != self.config.timeout:
                temp_llm = AzureChatOpenAI(
                    azure_endpoint=self.config.endpoint,
                    api_key=self.config.api_key,
                    api_version=self.config.api_version,
                    azure_deployment=self.config.deployment_name,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    timeout=timeout
                )
                llm_to_use = temp_llm
            else:
                llm_to_use = self.llm
            
            # Send request to AI model with timeout handling
            import signal
            import contextlib
            
            @contextlib.contextmanager
            def timeout_context(seconds):
                def signal_handler(signum, frame):
                    raise TimeoutError(f"AI request timed out after {seconds} seconds")
                
                # Set timeout handler (Unix only)
                old_handler = None
                if hasattr(signal, 'SIGALRM'):
                    old_handler = signal.signal(signal.SIGALRM, signal_handler)
                    signal.alarm(seconds)
                
                try:
                    yield
                finally:
                    if hasattr(signal, 'SIGALRM'):
                        signal.alarm(0)
                        if old_handler:
                            signal.signal(signal.SIGALRM, old_handler)
            
            # Try with timeout context (Unix) or direct timeout (Windows/others)
            try:
                with timeout_context(timeout):
                    response = llm_to_use.invoke([HumanMessage(content=prompt)])
            except (TimeoutError, Exception) as timeout_error:
                # Fallback for systems that don't support signal-based timeout
                if "timeout" not in str(timeout_error).lower():
                    raise  # Re-raise if not a timeout error
                
                ai_logger.warning(f"AI request timed out after {timeout}s, retrying with shorter prompt", extra={
                    'component': 'ai_service',
                    'batch_number': batch_number,
                    'timeout': timeout
                })
                
                # Try with a simplified prompt if timeout occurred
                simplified_prompt = self._create_simplified_prompt(prompt)
                if simplified_prompt and len(simplified_prompt) < len(prompt) * 0.7:
                    response = llm_to_use.invoke([HumanMessage(content=simplified_prompt)])
                else:
                    raise TimeoutError(f"AI request timed out after {timeout} seconds")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Create response object
            ai_response = AIModelResponse(
                content=response.content.strip(),
                model_name=self.config.deployment_name,
                prompt_tokens=0,  # Not available from LangChain
                completion_tokens=0,  # Not available from LangChain
                total_tokens=0,  # Not available from LangChain
                response_time=response_time,
                success=True
            )
            
            ai_logger.log_ai_interaction(
                prompt_length=len(prompt),
                response_length=len(ai_response.content),
                model_name=self.config.deployment_name,
                success=True,
                duration=response_time
            )
            
            log_function_exit(ai_logger, "send_analysis_request", 
                            f"Response received: {len(ai_response.content)} chars in {response_time:.2f}s")
            
            return ai_response
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            error_response = AIModelResponse(
                content="",
                model_name=self.config.deployment_name,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                response_time=response_time,
                success=False,
                error_message=str(e)
            )
            
            ai_logger.log_ai_interaction(
                prompt_length=len(prompt),
                response_length=0,
                model_name=self.config.deployment_name,
                success=False,
                duration=response_time
            )
            
            ai_logger.error("AI model request failed", extra={
                'component': 'ai_service',
                'batch_number': batch_number,
                'error': str(e),
                'response_time': response_time
            })
            
            return error_response
    
    def _create_simplified_prompt(self, original_prompt: str) -> Optional[str]:
        """Create a simplified version of the prompt for timeout recovery"""
        try:
            # Extract key parts of the original prompt
            if "**Tables to Analyze:**" in original_prompt:
                parts = original_prompt.split("**Tables to Analyze:**")
                if len(parts) >= 2:
                    pre_tables = parts[0]
                    tables_section = parts[1]
                    
                    # Limit to first 2 tables only
                    table_lines = tables_section.split('\n')
                    simplified_lines = []
                    table_count = 0
                    
                    for line in table_lines:
                        if line.strip().startswith('**Table:'):
                            table_count += 1
                            if table_count > 2:
                                break
                        simplified_lines.append(line)
                    
                    simplified_tables = '\n'.join(simplified_lines[:50])  # Limit lines too
                    
                    # Create simplified prompt
                    simplified_prompt = f"""{pre_tables.split('**CRITICAL INSTRUCTIONS:**')[0]}
**CRITICAL INSTRUCTIONS:**
1. Analyze ONLY the first 2 tables shown below
2. Return ONLY valid JSON with no additional text
3. Be concise in explanations

**Tables to Analyze:**
{simplified_tables}

Return analysis as JSON only."""
                    
                    return simplified_prompt
            
            return None
            
        except Exception:
            return None


class JSONExtractor:
    """Handles JSON extraction from AI responses"""
    
    def __init__(self):
        self.extraction_attempts = []
    
    def extract_json_from_response(self, response: AIModelResponse) -> Optional[Dict[str, Any]]:
        """Extract JSON from AI response using multiple methods"""
        log_function_entry(ai_logger, "extract_json_from_response", 
                          response_length=len(response.content))
        
        self.extraction_attempts.clear()
        
        # Check for truncation first
        if self._is_response_truncated(response.content):
            ai_logger.warning("Response appears to be truncated", extra={
                'component': 'json_extractor',
                'response_length': len(response.content)
            })
            return None
        
        # Try multiple extraction methods
        extraction_methods = [
            ("Balanced braces", self._extract_balanced_json),
            ("Regex pattern", self._extract_regex_json),
            ("Advanced extraction", self._extract_advanced_json),
            ("Simple extraction", self._extract_simple_json)
        ]
        
        for method_name, method_func in extraction_methods:
            attempt = self._try_extraction_method(method_name, method_func, response.content)
            self.extraction_attempts.append(attempt)
            
            if attempt.success:
                ai_logger.log_json_parsing_attempt(
                    response_length=len(response.content),
                    method=method_name,
                    success=True
                )
                
                log_function_exit(ai_logger, "extract_json_from_response", 
                                f"Success with {method_name}")
                return json.loads(attempt.extracted_content)
        
        # Try JSON repair as last resort
        repaired_json = self._attempt_json_repair(response.content)
        if repaired_json:
            ai_logger.log_json_parsing_attempt(
                response_length=len(response.content),
                method="JSON repair",
                success=True
            )
            
            log_function_exit(ai_logger, "extract_json_from_response", "Success with JSON repair")
            return repaired_json
        
        # Log all failed attempts
        for attempt in self.extraction_attempts:
            ai_logger.log_json_parsing_attempt(
                response_length=len(response.content),
                method=attempt.method,
                success=False,
                error=attempt.error_message
            )
        
        ai_logger.error("All JSON extraction methods failed", extra={
            'component': 'json_extractor',
            'response_length': len(response.content),
            'attempts': len(self.extraction_attempts)
        })
        
        log_function_exit(ai_logger, "extract_json_from_response", "All methods failed")
        return None
    
    def _try_extraction_method(self, method_name: str, method_func, response_text: str) -> JSONExtractionAttempt:
        """Try a single extraction method and record the attempt"""
        start_time = time.time()
        
        try:
            ai_logger.debug(f"Trying {method_name} extraction", extra={
                'component': 'json_extractor',
                'method': method_name
            })
            
            extracted_content = method_func(response_text)
            
            if extracted_content:
                # Try to parse to validate
                json.loads(extracted_content)
                processing_time = time.time() - start_time
                
                return JSONExtractionAttempt(
                    method=method_name,
                    success=True,
                    extracted_content=extracted_content,
                    error_message=None,
                    processing_time=processing_time
                )
            else:
                processing_time = time.time() - start_time
                return JSONExtractionAttempt(
                    method=method_name,
                    success=False,
                    extracted_content=None,
                    error_message="No JSON content extracted",
                    processing_time=processing_time
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            return JSONExtractionAttempt(
                method=method_name,
                success=False,
                extracted_content=None,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def _is_response_truncated(self, response_text: str) -> bool:
        """Check if the AI response appears to be truncated"""
        # Check if JSON structure is incomplete by counting braces/brackets
        open_braces = response_text.count('{')
        close_braces = response_text.count('}')
        open_brackets = response_text.count('[')
        close_brackets = response_text.count(']')
        
        if open_braces != close_braces or open_brackets != close_brackets:
            return True
        
        # Get the last 100 characters to check for truncation patterns
        tail = response_text[-100:].strip()
        
        # Check for specific truncation patterns
        critical_truncation_patterns = [
            r'"column_name":\s*$',
            r'"data_type":\s*$',
            r'"is_sensitive":\s*$',
            r'"risk_explanation":\s*$',
            r'"applicable_regulations":\s*$',
            r'\{\s*$',
            r'\[\s*$',
            r':\s*$',
            r',\s*$',
            r'"\s*:\s*$',
            r'"\s*,\s*$',
        ]
        
        for pattern in critical_truncation_patterns:
            if re.search(pattern, tail):
                return True
        
        # Check for incomplete string values
        if re.search(r'"\s*:\s*"[^"]*$', tail):
            return True
        
        # Check if we have a complete JSON structure
        if not re.search(r'}\s*$', response_text):
            return True
        
        return False
    
    def _extract_balanced_json(self, text: str) -> Optional[str]:
        """Extract JSON using balanced brace counting"""
        start_idx = text.find('{')
        if start_idx == -1:
            return None
            
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start_idx, len(text)):
            char = text[i]
            
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
                
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return text[start_idx:i+1]
        return None
    
    def _extract_regex_json(self, text: str) -> Optional[str]:
        """Extract JSON using regex patterns"""
        patterns = [
            r'\{[^{}]*"batch_analysis"[^{}]*"table_results"[^{}]*\[[^\]]*\][^{}]*\}',
            r'\{.*?"table_results".*?\[.*?\].*?\}',
            r'\{.*?"table_results".*?\}',
        ]
        
        for pattern in patterns:
            try:
                matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
                if matches:
                    for match in matches:
                        try:
                            json.loads(match)
                            return match
                        except json.JSONDecodeError:
                            continue
            except Exception:
                continue
        return None
    
    def _extract_advanced_json(self, text: str) -> Optional[str]:
        """Advanced JSON extraction with markdown handling"""
        # Remove markdown code blocks
        text = re.sub(r'```[a-zA-Z]*\n(.*?)\n```', r'\1', text, flags=re.DOTALL)
        
        # Find JSON-like structures
        start_pos = 0
        while True:
            start_idx = text.find('{', start_pos)
            if start_idx == -1:
                break
                
            # Try balanced extraction from this position
            candidate = self._extract_balanced_json(text[start_idx:])
            if candidate and '"table_results"' in candidate:
                return candidate
                
            start_pos = start_idx + 1
        
        return None
    
    def _extract_simple_json(self, text: str) -> Optional[str]:
        """Simple JSON extraction as fallback"""
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        return None
    
    def _attempt_json_repair(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Attempt to repair common JSON formatting issues"""
        try:
            # Remove everything before first { and after last }
            start_idx = response_text.find('{')
            if start_idx == -1:
                return None
                
            end_idx = response_text.rfind('}')
            if end_idx == -1:
                return None
                
            cleaned_text = response_text[start_idx:end_idx + 1]
            
            # Fix common JSON issues
            repair_patterns = [
                (r',\s*}', '}'),  # Remove trailing commas before }
                (r',\s*]', ']'),  # Remove trailing commas before ]
                (r'}\s*\n\s*{', '},\n        {'),  # Fix missing commas between objects
                (r']\s*\n\s*{', '],\n        {'),  # Fix missing commas between array and object
                (r'}\s*\n\s*\[', '},['),  # Fix missing commas between object and array
                (r'"\s*\n\s*"', '",\n        "'),  # Fix missing commas between strings
                (r'(\]|\})\s*\n\s*(\{|\[)', r'\1,\n        \2'),  # General missing comma fix
            ]
            
            for pattern, replacement in repair_patterns:
                cleaned_text = re.sub(pattern, replacement, cleaned_text)
            
            # Try to parse the repaired JSON
            return json.loads(cleaned_text)
            
        except Exception:
            return None


# Global service instances
ai_service = AIService()
json_extractor = JSONExtractor()