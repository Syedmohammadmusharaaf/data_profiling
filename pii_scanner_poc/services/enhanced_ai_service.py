#!/usr/bin/env python3
"""
Enhanced AI Service with Type Hints and Improved Architecture
AI service for LLM-based PII/PHI classification with proper typing
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple, Protocol
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod

try:
    import openai
    from openai import AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import our core systems
from pii_scanner_poc.core.service_interfaces import AIServiceInterface, ServiceStatus
from pii_scanner_poc.core.exceptions import AIServiceError, AIServiceUnavailableError, AIServiceTimeoutError
from pii_scanner_poc.core.configuration import SystemConfig
from pii_scanner_poc.models.data_models import ColumnMetadata, PIIType, RiskLevel, Regulation


@dataclass
class AIUsageMetrics:
    """Data class for AI service usage metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    last_request_time: Optional[datetime] = None


@dataclass
class AIAnalysisResult:
    """Data class for AI analysis results"""
    field_name: str
    pii_type: PIIType
    risk_level: RiskLevel
    confidence_score: float
    applicable_regulations: List[Regulation]
    rationale: str
    processing_time: float
    tokens_used: int


class PromptTemplate(Protocol):
    """Protocol for prompt template implementations"""
    
    def generate_prompt(self, 
                       columns: List[Dict[str, Any]], 
                       regulation: str,
                       context: Optional[Dict[str, Any]] = None) -> str:
        """Generate AI prompt for column analysis"""
        ...


class PIIAnalysisPromptTemplate:
    """Enhanced prompt template for PII analysis with better structure"""
    
    def __init__(self, config: SystemConfig):
        """
        Initialize prompt template
        
        Args:
            config: System configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def generate_prompt(self, 
                       columns: List[Dict[str, Any]], 
                       regulation: str,
                       context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate structured prompt for PII/PHI analysis
        
        Args:
            columns: List of column metadata dictionaries
            regulation: Target regulation (GDPR, HIPAA, CCPA)
            context: Optional additional context
            
        Returns:
            str: Generated prompt text
        """
        context = context or {}
        
        # Base prompt with clear instructions
        prompt = f"""You are an expert privacy compliance analyst specializing in {regulation} regulation.

TASK: Analyze the following database columns and identify potential PII/PHI fields according to {regulation} requirements.

ANALYSIS CRITERIA for {regulation}:
"""
        
        # Add regulation-specific criteria
        if regulation == "GDPR":
            prompt += """
- Personal Data: Any information relating to an identified or identifiable person
- Special Categories: Health, genetic, biometric, racial, ethnic, political, religious data
- Risk Levels: HIGH (special categories), MEDIUM (identifiers), LOW (descriptive)
"""
        elif regulation == "HIPAA":
            prompt += """
- PHI: Any information that identifies an individual and relates to health status
- Safe Harbor Identifiers: 18 specific types of identifiers that must be removed
- Risk Levels: HIGH (direct identifiers), MEDIUM (quasi-identifiers), LOW (aggregated)
"""
        elif regulation == "CCPA":
            prompt += """
- Personal Information: Information that identifies, relates to, or is reasonably capable of being associated with a consumer
- Sensitive Personal Information: Specific categories requiring additional protection
- Risk Levels: HIGH (sensitive), MEDIUM (identifiers), LOW (publicly available)
"""
        
        prompt += f"""
COLUMNS TO ANALYZE:
"""
        
        # Add column information
        for i, column in enumerate(columns, 1):
            prompt += f"""
{i}. Column: {column.get('column_name', 'unknown')}
   Table: {column.get('table_name', 'unknown')}
   Data Type: {column.get('data_type', 'unknown')}"""
            
            if column.get('constraints'):
                prompt += f"\n   Constraints: {column['constraints']}"
            
            if context.get('table_context'):
                other_columns = [col for col in context['table_context'] 
                               if col != column.get('column_name')]
                if other_columns:
                    prompt += f"\n   Related Columns: {', '.join(other_columns[:5])}"
        
        # Output format instructions
        prompt += """

OUTPUT FORMAT:
Respond with a JSON array containing one object per column with this exact structure:
[
  {
    "column_name": "exact_column_name",
    "pii_type": "EMAIL|PHONE|NAME|ADDRESS|SSN|MEDICAL|FINANCIAL|ID|BIOMETRIC|OTHER|NONE",
    "risk_level": "HIGH|MEDIUM|LOW",
    "confidence_score": 0.0-1.0,
    "applicable_regulations": ["GDPR", "HIPAA", "CCPA"],
    "rationale": "Brief explanation for classification",
    "is_sensitive": true/false
  }
]

IMPORTANT RULES:
1. Use EXACT column names from the input
2. Confidence scores should reflect certainty (0.9+ for obvious cases, 0.5-0.8 for contextual, <0.5 for uncertain)
3. Rationale should be specific and reference {regulation} requirements
4. Include multiple regulations if applicable
5. Use "NONE" for clearly non-PII columns
6. Consider column context within the table

Analyze each column carefully and respond with valid JSON only:"""
        
        return prompt


class EnhancedAIService(AIServiceInterface):
    """
    Enhanced AI service implementation with proper typing and error handling
    
    Provides LLM-based PII/PHI classification with comprehensive metrics,
    error handling, and performance optimization.
    """
    
    def __init__(self, config: SystemConfig):
        """
        Initialize Enhanced AI Service
        
        Args:
            config: System configuration
        """
        super().__init__(config, "enhanced_ai_service")
        
        self.client: Optional[AzureOpenAI] = None
        self.prompt_template = PIIAnalysisPromptTemplate(config)
        self.usage_metrics = AIUsageMetrics()
        
        # Configuration shortcuts
        self.ai_config = config.ai_service
        self.processing_config = config.processing
        
        # Request tracking
        self._request_times: List[float] = []
        self._max_tracked_requests = 100
    
    def initialize(self) -> bool:
        """
        Initialize the AI service
        
        Returns:
            bool: True if initialization successful
        """
        try:
            if not OPENAI_AVAILABLE:
                raise AIServiceError("OpenAI package not available")
            
            if not self.ai_config.api_key:
                raise AIServiceError("AI service API key not configured")
            
            # Initialize Azure OpenAI client
            self.client = AzureOpenAI(
                api_key=self.ai_config.api_key,
                api_version="2024-02-01",
                azure_endpoint=self.ai_config.api_base,
                timeout=self.ai_config.timeout,
                max_retries=self.ai_config.max_retries
            )
            
            # Test connection
            if not self.validate_connection():
                raise AIServiceError("Failed to validate AI service connection")
            
            self._update_status(ServiceStatus.READY)
            self.logger.info("Enhanced AI service initialized successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize AI service: {e}"
            self.logger.error(error_msg)
            self._update_status(ServiceStatus.ERROR, error_msg)
            return False
    
    def shutdown(self) -> bool:
        """
        Shutdown the AI service
        
        Returns:
            bool: True if shutdown successful
        """
        try:
            self.client = None
            self._update_status(ServiceStatus.STOPPED)
            self.logger.info("Enhanced AI service shutdown completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during AI service shutdown: {e}")
            return False
    
    def analyze_columns_for_pii(self, 
                               columns: List[Dict[str, Any]], 
                               regulation: str,
                               timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze columns for PII/PHI content using AI
        
        Args:
            columns: List of column metadata dictionaries
            regulation: Target regulation (GDPR, HIPAA, CCPA)
            timeout: Optional timeout in seconds
            
        Returns:
            Dict containing analysis results
            
        Raises:
            AIServiceError: If analysis fails
            AIServiceTimeoutError: If request times out
            AIServiceUnavailableError: If service is unavailable
        """
        if not self.client:
            raise AIServiceUnavailableError("enhanced_ai_service")
        
        start_time = time.time()
        timeout = timeout or self.ai_config.timeout
        
        try:
            # Generate prompt
            prompt = self._generate_analysis_prompt(columns, regulation)
            
            # Make API request with timeout
            response = self._make_ai_request(prompt, timeout)
            
            # Parse and validate response
            results = self._parse_ai_response(response, columns)
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_metrics(True, processing_time, response.usage.total_tokens if hasattr(response, 'usage') else 0)
            
            return {
                'results': results,
                'metadata': {
                    'regulation': regulation,
                    'processing_time': processing_time,
                    'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0,
                    'model': self.ai_config.model,
                    'confidence_threshold': self.processing_config.confidence_threshold
                }
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_metrics(False, processing_time, 0)
            
            if "timeout" in str(e).lower():
                raise AIServiceTimeoutError(timeout)
            else:
                raise AIServiceError(f"AI analysis failed: {e}")
    
    def _generate_analysis_prompt(self, 
                                 columns: List[Dict[str, Any]], 
                                 regulation: str) -> str:
        """
        Generate AI prompt for analysis
        
        Args:
            columns: Column metadata
            regulation: Target regulation
            
        Returns:
            str: Generated prompt
        """
        # Extract table context for better analysis
        table_context = {}
        for column in columns:
            table_name = column.get('table_name', 'unknown')
            if table_name not in table_context:
                table_context[table_name] = []
            table_context[table_name].append(column.get('column_name', 'unknown'))
        
        context = {
            'table_context': table_context,
            'total_columns': len(columns),
            'regulation': regulation
        }
        
        return self.prompt_template.generate_prompt(columns, regulation, context)
    
    def _make_ai_request(self, prompt: str, timeout: int) -> Any:
        """
        Make request to AI service
        
        Args:
            prompt: Generated prompt
            timeout: Request timeout
            
        Returns:
            AI service response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.ai_config.model,
                messages=[
                    {"role": "system", "content": "You are an expert privacy compliance analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.ai_config.max_tokens,
                temperature=self.ai_config.temperature,
                timeout=timeout
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"AI request failed: {e}")
            raise AIServiceError(f"AI request failed: {e}")
    
    def _parse_ai_response(self, 
                          response: Any, 
                          columns: List[Dict[str, Any]]) -> List[AIAnalysisResult]:
        """
        Parse and validate AI response
        
        Args:
            response: AI service response
            columns: Original column metadata
            
        Returns:
            List of analysis results
        """
        try:
            # Extract content from response
            content = response.choices[0].message.content.strip()
            
            # Simple JSON extraction with fallback (avoiding method dependency issues)
            import re
            import json
            
            # Try to find JSON in code blocks first
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', content, re.DOTALL)
            if json_match:
                json_content = json_match.group(1)
            else:
                # Try to find any JSON array
                json_match = re.search(r'(\[.*?\])', content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1)
                else:
                    json_content = content
            
            # Parse JSON with basic error handling
            try:
                parsed_results = json.loads(json_content)
                if not isinstance(parsed_results, list):
                    parsed_results = [parsed_results] if parsed_results else []
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON parsing failed: {e}")
                print(f"Failed to parse AI response: {str(e)}")
                parsed_results = []
            
            if not isinstance(parsed_results, list):
                raise ValueError("Response must be a JSON array")
            
            # Convert to structured results
            results = []
            for i, result in enumerate(parsed_results):
                try:
                    # Map to our data structures with error handling
                    # Safe enum conversion inline (global instance compatibility)
                    pii_type_val = result.get('pii_type', 'OTHER')
                    try:
                        if isinstance(pii_type_val, str):
                            # Try direct value match
                            for enum_member in PIIType:
                                if enum_member.value.upper() == pii_type_val.upper():
                                    pii_type = enum_member
                                    break
                            else:
                                # Try name match
                                for enum_member in PIIType:
                                    if enum_member.name.upper() == pii_type_val.upper():
                                        pii_type = enum_member
                                        break
                                else:
                                    pii_type = PIIType(pii_type_val)
                        else:
                            pii_type = PIIType(pii_type_val)
                    except (ValueError, AttributeError):
                        pii_type = PIIType.OTHER  # default
                    
                    risk_level_val = result.get('risk_level', 'LOW')
                    try:
                        if isinstance(risk_level_val, str):
                            # Try direct value match
                            for enum_member in RiskLevel:
                                if enum_member.value.upper() == risk_level_val.upper():
                                    risk_level = enum_member
                                    break
                            else:
                                # Try name match
                                for enum_member in RiskLevel:
                                    if enum_member.name.upper() == risk_level_val.upper():
                                        risk_level = enum_member
                                        break
                                else:
                                    risk_level = RiskLevel(risk_level_val)
                        else:
                            risk_level = RiskLevel(risk_level_val)
                    except (ValueError, AttributeError):
                        risk_level = RiskLevel.LOW  # default
                    
                    # Parse regulations
                    regulations = []
                    for reg in result.get('applicable_regulations', []):
                        try:
                            regulations.append(Regulation(reg))
                        except ValueError:
                            self.logger.warning(f"Unknown regulation: {reg}")
                    
                    analysis_result = AIAnalysisResult(
                        field_name=result.get('column_name', columns[i].get('column_name', 'unknown')),
                        pii_type=pii_type,
                        risk_level=risk_level,
                        confidence_score=float(result.get('confidence_score', 0.5)),
                        applicable_regulations=regulations,
                        rationale=result.get('rationale', 'AI analysis result'),
                        processing_time=0.0,  # Will be set by caller
                        tokens_used=0  # Will be set by caller
                    )
                    
                    results.append(analysis_result)
                    
                except Exception as e:
                    self.logger.warning(f"Error parsing result {i}: {e}")
                    # Create fallback result
                    fallback_result = AIAnalysisResult(
                        field_name=columns[i].get('column_name', 'unknown'),
                        pii_type=PIIType.OTHER,
                        risk_level=RiskLevel.LOW,
                        confidence_score=0.3,
                        applicable_regulations=[],
                        rationale=f"Parsing error: {e}",
                        processing_time=0.0,
                        tokens_used=0
                    )
                    results.append(fallback_result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI response: {e}")
            # Return fallback results for all columns
            fallback_results = []
            for column in columns:
                fallback_result = AIAnalysisResult(
                    field_name=column.get('column_name', 'unknown'),
                    pii_type=PIIType.OTHER,
                    risk_level=RiskLevel.LOW,
                    confidence_score=0.2,
                    applicable_regulations=[],
                    rationale=f"Response parsing failed: {e}",
                    processing_time=0.0,
                    tokens_used=0
                )
                fallback_results.append(fallback_result)
            
            return fallback_results
    
    def _update_metrics(self, success: bool, processing_time: float, tokens_used: int):
        """
        Update usage metrics
        
        Args:
            success: Whether request was successful
            processing_time: Time taken for processing
            tokens_used: Number of tokens used
        """
        self.usage_metrics.total_requests += 1
        
        if success:
            self.usage_metrics.successful_requests += 1
        else:
            self.usage_metrics.failed_requests += 1
        
        self.usage_metrics.total_tokens_used += tokens_used
        self.usage_metrics.last_request_time = datetime.now()
        
        # Update average response time
        self._request_times.append(processing_time)
        if len(self._request_times) > self._max_tracked_requests:
            self._request_times = self._request_times[-self._max_tracked_requests:]
        
        if self._request_times:
            self.usage_metrics.average_response_time = sum(self._request_times) / len(self._request_times)
        
        # Estimate cost (rough calculation for Azure OpenAI)
        cost_per_token = 0.00003  # Approximate cost
        self.usage_metrics.total_cost += tokens_used * cost_per_token
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Get AI service usage statistics
        
        Returns:
            Dict containing usage metrics
        """
        return {
            'total_requests': self.usage_metrics.total_requests,
            'successful_requests': self.usage_metrics.successful_requests,
            'failed_requests': self.usage_metrics.failed_requests,
            'success_rate': (self.usage_metrics.successful_requests / 
                           max(1, self.usage_metrics.total_requests)),
            'total_tokens_used': self.usage_metrics.total_tokens_used,
            'estimated_total_cost': self.usage_metrics.total_cost,
            'average_response_time': self.usage_metrics.average_response_time,
            'last_request_time': self.usage_metrics.last_request_time.isoformat() if self.usage_metrics.last_request_time else None,
            'model': self.ai_config.model,
            'current_status': self.get_status().value
        }
    
    def validate_connection(self) -> bool:
        """
        Validate connection to AI service
        
        Returns:
            bool: True if connection is valid
        """
        try:
            if not self.client:
                return False
            
            # Test with minimal request
            test_response = self.client.chat.completions.create(
                model=self.ai_config.model,
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=5,
                timeout=10
            )
            
            return test_response is not None
            
        except Exception as e:
            self.logger.error(f"Connection validation failed: {e}")
            return False


class PromptTemplateLibrary:
    """
    Library of prompt templates for different PII/PHI analysis scenarios.
    
    This class provides a collection of well-tested prompt templates that can be used
    for various types of data privacy analysis tasks including GDPR, HIPAA, and CCPA
    compliance assessments.
    """
    
    def __init__(self):
        """Initialize the prompt template library with default templates."""
        self.templates = {
            'basic_pii': self._get_basic_pii_template(),
            'healthcare': self._get_healthcare_template(),
            'financial': self._get_financial_template(),
            'gdpr': self._get_gdpr_template(),
            'hipaa': self._get_hipaa_template(),
            'ccpa': self._get_ccpa_template()
        }
    
    def get_template(self, template_name: str) -> str:
        """
        Get a prompt template by name.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            str: The prompt template text
            
        Raises:
            KeyError: If the template name is not found
        """
        if template_name not in self.templates:
            raise KeyError(f"Template '{template_name}' not found. Available templates: {list(self.templates.keys())}")
        
        return self.templates[template_name]
    
    def get_optimal_template(self, complexity: int, data_sensitivity: str, performance_priority: str) -> str:
        """
        Get an optimal prompt template based on analysis parameters.
        
        This method selects the most appropriate template based on the complexity
        of the data analysis task, the sensitivity of the data, and performance
        requirements.
        
        Args:
            complexity: Complexity level of the analysis (1-5, where 5 is most complex)
            data_sensitivity: Data sensitivity level ('low', 'medium', 'high', 'critical')
            performance_priority: Performance priority ('speed', 'accuracy', 'balanced')
            
        Returns:
            str: The optimal prompt template for the given parameters
        """
        # Simple logic to select appropriate template based on parameters
        if data_sensitivity.lower() in ['high', 'critical']:
            if complexity >= 4:
                return self.get_template('hipaa')  # Most comprehensive for high-sensitivity
            else:
                return self.get_template('gdpr')   # Good balance for medium complexity
        elif complexity >= 3:
            return self.get_template('basic_pii')  # General purpose for medium complexity
        else:
            return self.get_template('basic_pii')  # Simple template for low complexity
        
        # Fallback to basic template
        return self.get_template('basic_pii')
    
    def _get_basic_pii_template(self) -> str:
        """Get basic PII analysis template."""
        return """You are an expert privacy compliance analyst. Analyze the following database columns and identify potential PII fields.

For each column, provide:
1. PII Type classification
2. Risk level (LOW/MEDIUM/HIGH/CRITICAL)
3. Confidence score (0.0-1.0)
4. Brief rationale

Output in JSON format."""
    
    def _get_healthcare_template(self) -> str:
        """Get healthcare-specific template for HIPAA compliance."""
        return """You are a HIPAA compliance expert. Analyze these database columns for Protected Health Information (PHI).

Focus on:
- Direct identifiers (names, SSN, medical record numbers)
- Quasi-identifiers (dates, geographic data)
- Medical information (diagnoses, treatments)

Classify each column according to HIPAA requirements."""
    
    def _get_financial_template(self) -> str:
        """Get financial services template."""
        return """You are a financial privacy expert. Analyze these columns for financial PII and sensitive information.

Consider:
- Account numbers and payment information
- Credit scores and financial history
- Personal identifiers in financial context

Apply relevant financial privacy regulations."""
    
    def _get_gdpr_template(self) -> str:
        """Get GDPR-specific template."""
        return """You are a GDPR compliance specialist. Analyze these database columns for personal data under GDPR.

Categories to consider:
- Personal data (Article 4(1))
- Special categories (Article 9)
- Data relating to criminal convictions

Assess lawful basis requirements and data subject rights impact."""
    
    def _get_hipaa_template(self) -> str:
        """Get HIPAA-specific template."""
        return """You are a HIPAA Privacy Officer. Analyze these columns for Protected Health Information.

18 HIPAA identifiers to consider:
- Names, addresses, dates
- Phone/fax numbers, email addresses
- Social Security numbers
- Medical record numbers
- Health plan beneficiary numbers
- Account numbers, certificate/license numbers
- Vehicle identifiers and serial numbers
- Device identifiers and serial numbers
- Web URLs and IP addresses
- Biometric identifiers
- Full face photos and comparable images
- Any other unique identifying number, characteristic, or code

Determine if data requires HIPAA safeguards."""
    
    def _get_ccpa_template(self) -> str:
        """Get CCPA-specific template."""
        return """You are a CCPA compliance expert. Analyze these columns for personal information under California Consumer Privacy Act.

CCPA personal information categories:
- Identifiers (real name, alias, postal address, unique personal identifier, online identifier, IP address, email address, account name, SSN, driver's license number, passport number, or other similar identifiers)
- Personal information categories listed in the California Customer Records statute
- Protected classification characteristics under California or federal law
- Commercial information
- Biometric information
- Internet or other similar network activity
- Geolocation data
- Sensory data
- Professional or employment-related information
- Non-public education information
- Inferences drawn from other personal information

Assess consumer rights implications and business purpose limitations."""


    def _extract_json_basic(self, content: str) -> str:
        """Basic JSON extraction for backward compatibility"""
        import re
        
        # Try to find JSON in code blocks first
        json_match = re.search(r'```json\s*(\[.*?\])\s*```', content, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # Try to find any JSON array
        json_match = re.search(r'(\[.*?\])', content, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # Return the content as-is if no JSON pattern found
        return content
    
    def _parse_json_basic(self, json_content: str) -> list:
        """Basic JSON parsing for backward compatibility"""
        import json
        
        try:
            result = json.loads(json_content)
            return result if isinstance(result, list) else [result]
        except json.JSONDecodeError as e:
            self.logger.warning(f"Basic JSON parsing failed: {e}")
            print(f"Failed to parse AI response: {str(e)}")
            return []

    def _extract_json_content(self, content: str) -> str:
        """
        Extract JSON content from AI response with multiple fallback strategies
        
        Args:
            content: Raw AI response content
            
        Returns:
            Extracted JSON content string
        """
        import re
        
        # Strategy 1: Look for JSON code blocks
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            if json_end > json_start:
                return content[json_start:json_end].strip()
        
        # Strategy 2: Look for plain JSON arrays/objects
        if content.startswith('[') and content.endswith(']'):
            return content
        if content.startswith('{') and content.endswith('}'):
            return content
        
        # Strategy 3: Find JSON array anywhere in content
        json_array_match = re.search(r'\[[\s\S]*?\]', content)
        if json_array_match:
            return json_array_match.group().strip()
        
        # Strategy 4: Find JSON object anywhere in content
        json_object_match = re.search(r'\{[\s\S]*?\}', content)
        if json_object_match:
            return json_object_match.group().strip()
        
        # Strategy 5: Look for JSON-like structure without proper formatting
        # Remove common text artifacts
        cleaned_content = re.sub(r'^[^[{]*', '', content)  # Remove text before JSON
        cleaned_content = re.sub(r'[^}\]]*$', '', cleaned_content)  # Remove text after JSON
        
        if cleaned_content and (cleaned_content.startswith('[') or cleaned_content.startswith('{')):
            return cleaned_content
        
        raise ValueError("No valid JSON structure found in AI response")
    
    def _parse_json_with_recovery(self, json_content: str) -> list:
        """
        Parse JSON with error recovery mechanisms
        
        Args:
            json_content: JSON content string
            
        Returns:
            Parsed JSON data
        """
        import json
        import re
        
        # Attempt 1: Direct parsing
        try:
            result = json.loads(json_content)
            return result if isinstance(result, list) else [result]
        except json.JSONDecodeError as e:
            self.logger.warning(f"Initial JSON parsing failed: {e}")
        
        # Attempt 2: Fix common JSON issues
        try:
            # Fix unterminated strings
            fixed_content = self._fix_json_string_termination(json_content)
            result = json.loads(fixed_content)
            return result if isinstance(result, list) else [result]
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON repair attempt failed: {e}")
        
        # Attempt 3: Extract partial valid JSON
        try:
            partial_json = self._extract_partial_json(json_content)
            result = json.loads(partial_json)
            return result if isinstance(result, list) else [result]
        except json.JSONDecodeError as e:
            self.logger.warning(f"Partial JSON extraction failed: {e}")
        
        # Fallback: Return empty list and log the issue
        self.logger.error(f"Failed to parse AI response: {json_content[:200]}...")
        print(f"Failed to parse AI response: {str(e)}")
        return []
    
    def _fix_json_string_termination(self, json_content: str) -> str:
        """Fix common JSON string termination issues"""
        import re
        
        # Fix unterminated strings at the end
        if json_content.count('"') % 2 != 0:
            # Find the last unterminated string and close it
            last_quote = json_content.rfind('"')
            if last_quote != -1:
                # Check if it's already properly terminated
                after_quote = json_content[last_quote + 1:].strip()
                if not after_quote.startswith(',') and not after_quote.startswith('}') and not after_quote.startswith(']'):
                    # Add closing quote before next structural element
                    json_content = json_content[:last_quote + 1] + '"' + json_content[last_quote + 1:]
        
        return json_content
    
    def _extract_partial_json(self, json_content: str) -> str:
        """Extract the largest valid JSON portion"""
        import json
        
        # Try to find the largest valid JSON array
        if json_content.startswith('['):
            for i in range(len(json_content), 0, -1):
                try:
                    partial = json_content[:i]
                    if partial.endswith(']'):
                        json.loads(partial)
                        return partial
                except json.JSONDecodeError:
                    continue
        
        return json_content
    
    def _safe_enum_conversion(self, enum_class, value):
        """Safely convert value to enum with fallback"""
        try:
            if isinstance(value, str):
                # Try direct value match
                for enum_member in enum_class:
                    if enum_member.value.upper() == value.upper():
                        return enum_member
                # Try name match
                for enum_member in enum_class:
                    if enum_member.name.upper() == value.upper():
                        return enum_member
            return enum_class(value)
        except (ValueError, AttributeError):
            # Return default value for the enum
            return list(enum_class)[0]


# Global enhanced AI service instance
try:
    from pii_scanner_poc.core.configuration import get_config
    system_config = get_config()
    enhanced_ai_service = EnhancedAIService(system_config)
    # Initialize the service
    enhanced_ai_service.initialize()
except ImportError:
    # Fallback for when configuration is not available
    enhanced_ai_service = None