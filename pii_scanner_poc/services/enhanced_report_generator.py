#!/usr/bin/env python3
"""
Enhanced Report Generator for PII/PHI Scanner
Creates comprehensive, informative reports with detailed explanations and regulatory compliance information
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid

from pii_scanner_poc.models.enhanced_data_models import HybridClassificationSession, EnhancedFieldAnalysis
from pii_scanner_poc.models.data_models import Regulation, PIIType, RiskLevel
from pii_scanner_poc.utils.comprehensive_logger import comprehensive_logger

@dataclass
class RegulationInfo:
    """Detailed regulation information for enhanced reporting"""
    name: str
    full_name: str
    description: str
    key_requirements: List[str]
    penalties: str
    scope: str
    
@dataclass
class PIITypeInfo:
    """Comprehensive PII type information with detailed explanations"""
    pii_type: str
    category: str
    description: str
    sensitivity_level: str
    common_examples: List[str]
    regulations: List[str]
    protection_requirements: List[str]
    risk_factors: List[str]

class EnhancedReportGenerator:
    """
    Generate comprehensive, user-friendly reports with detailed explanations
    
    Features:
    - Detailed field-level explanations of why data is considered sensitive
    - Comprehensive regulation mapping with requirements
    - Risk assessment with actionable recommendations
    - Executive summary for business stakeholders
    - Technical details for compliance teams
    - Visual data for dashboard integration
    """
    
    def __init__(self):
        """Initialize enhanced report generator with comprehensive knowledge base"""
        self.regulation_info = self._load_regulation_info()
        self.pii_type_info = self._load_pii_type_info()
        comprehensive_logger.info("Enhanced report generator initialized", 
                                 component="report_generator", operation="init")
    
    def _load_regulation_info(self) -> Dict[str, RegulationInfo]:
        """Load comprehensive regulation information"""
        return {
            "HIPAA": RegulationInfo(
                name="HIPAA",
                full_name="Health Insurance Portability and Accountability Act",
                description="US federal law designed to protect sensitive patient health information from being disclosed without patient consent or knowledge.",
                key_requirements=[
                    "Implement administrative, physical, and technical safeguards",
                    "Conduct regular risk assessments and audits",
                    "Provide employee training on PHI handling",
                    "Establish business associate agreements",
                    "Implement access controls and audit logs",
                    "Ensure data encryption for electronic PHI"
                ],
                penalties="Fines ranging from $100 to $50,000+ per violation, with maximum annual penalties of $1.5 million",
                scope="Covered entities (healthcare providers, health plans, healthcare clearinghouses) and their business associates"
            ),
            "GDPR": RegulationInfo(
                name="GDPR",
                full_name="General Data Protection Regulation",
                description="EU regulation that protects personal data and privacy rights of EU residents, with global applicability for organizations processing EU resident data.",
                key_requirements=[
                    "Obtain explicit consent for data processing",
                    "Implement privacy by design and by default",
                    "Conduct Data Protection Impact Assessments (DPIAs)",
                    "Provide data subject rights (access, rectification, erasure)",
                    "Report data breaches within 72 hours",
                    "Appoint Data Protection Officers where required"
                ],
                penalties="Fines up to €20 million or 4% of annual global turnover, whichever is higher",
                scope="All organizations processing personal data of EU residents, regardless of organization location"
            ),
            "CCPA": RegulationInfo(
                name="CCPA",
                full_name="California Consumer Privacy Act",
                description="California state law that provides consumers with rights regarding their personal information and requires businesses to be transparent about data collection practices.",
                key_requirements=[
                    "Provide clear privacy notices and policies",
                    "Honor consumer rights requests (know, delete, opt-out)",
                    "Implement reasonable security measures",
                    "Obtain opt-in consent for sensitive personal information",
                    "Provide non-discrimination for exercising privacy rights",
                    "Maintain records of consumer requests and responses"
                ],
                penalties="Civil penalties up to $2,500 per violation or $7,500 for intentional violations",
                scope="Businesses that collect personal information of California residents and meet certain thresholds"
            )
        }
    
    def _load_pii_type_info(self) -> Dict[str, PIITypeInfo]:
        """Load comprehensive PII type information with detailed explanations"""
        return {
            "EMAIL": PIITypeInfo(
                pii_type="EMAIL",
                category="Contact Information",
                description="Electronic mail addresses that can uniquely identify individuals and be used for direct communication",
                sensitivity_level="HIGH",
                common_examples=["john.doe@company.com", "user123@gmail.com", "patient@hospital.org"],
                regulations=["GDPR", "CCPA", "HIPAA"],
                protection_requirements=[
                    "Encrypt in transit and at rest",
                    "Implement access controls",
                    "Log access and modifications",
                    "Provide consent mechanisms for marketing use"
                ],
                risk_factors=[
                    "Direct identification of individuals",
                    "Potential for spam and phishing attacks",
                    "Cross-system correlation possibilities",
                    "Marketing and privacy implications"
                ]
            ),
            "NAME": PIITypeInfo(
                pii_type="NAME",
                category="Personal Identifiers",
                description="First names, last names, and full names that directly identify individuals",
                sensitivity_level="HIGH",
                common_examples=["John Smith", "Maria Rodriguez", "Dr. Robert Johnson"],
                regulations=["GDPR", "CCPA", "HIPAA"],
                protection_requirements=[
                    "Implement data minimization principles",
                    "Provide anonymization/pseudonymization options",
                    "Enable data subject access and correction rights",
                    "Secure storage and transmission"
                ],
                risk_factors=[
                    "Direct personal identification",
                    "Social engineering potential",
                    "Identity theft risks",
                    "Discrimination possibilities"
                ]
            ),
            "SSN": PIITypeInfo(
                pii_type="SSN",
                category="Government Identifiers",
                description="Social Security Numbers used for identification and government services in the United States",
                sensitivity_level="CRITICAL",
                common_examples=["123-45-6789", "987654321", "SSN: 555-12-3456"],
                regulations=["HIPAA", "CCPA", "SOX", "GLBA"],
                protection_requirements=[
                    "Strongest encryption standards (AES-256)",
                    "Strict access controls with multi-factor authentication",
                    "Comprehensive audit logging",
                    "Regular security assessments",
                    "Secure disposal procedures"
                ],
                risk_factors=[
                    "Identity theft and fraud",
                    "Financial account access",
                    "Government benefit fraud",
                    "Credit report manipulation",
                    "Tax fraud possibilities"
                ]
            ),
            "PHONE": PIITypeInfo(
                pii_type="PHONE",
                category="Contact Information",
                description="Telephone numbers including mobile, landline, and international formats",
                sensitivity_level="MEDIUM",
                common_examples=["+1-555-123-4567", "(555) 987-6543", "555.123.4567"],
                regulations=["GDPR", "CCPA", "TCPA"],
                protection_requirements=[
                    "Consent for marketing communications",
                    "Opt-out mechanisms for calls/texts",
                    "Secure storage and access logging",
                    "Data retention policies"
                ],
                risk_factors=[
                    "Unwanted marketing communications",
                    "Social engineering attacks",
                    "Location tracking potential",
                    "Cross-reference with other data"
                ]
            ),
            "FINANCIAL": PIITypeInfo(
                pii_type="FINANCIAL",
                category="Financial Information",
                description="Credit card numbers, bank account details, and other financial identifiers",
                sensitivity_level="CRITICAL",
                common_examples=["4532-1234-5678-9012", "ACCT: 123456789", "IBAN: GB29NWBK60161331926819"],
                regulations=["PCI-DSS", "GLBA", "GDPR", "CCPA"],
                protection_requirements=[
                    "PCI-DSS compliance requirements",
                    "End-to-end encryption",
                    "Tokenization where possible",
                    "Strict access controls and monitoring",
                    "Regular security testing"
                ],
                risk_factors=[
                    "Financial fraud and theft",
                    "Unauthorized transactions",
                    "Credit damage",
                    "Account takeover attacks"
                ]
            ),
            "MEDICAL_ID": PIITypeInfo(
                pii_type="MEDICAL_ID",
                category="Healthcare Identifiers",
                description="Medical record numbers, patient IDs, and healthcare-specific identifiers",
                sensitivity_level="HIGH",
                common_examples=["MRN: 123456", "Patient ID: P789012", "Medical Record: MR-2023-001"],
                regulations=["HIPAA", "HITECH", "GDPR"],
                protection_requirements=[
                    "HIPAA-compliant access controls",
                    "Audit logging of all access",
                    "Minimum necessary principle",
                    "Business associate agreements",
                    "Breach notification procedures"
                ],
                risk_factors=[
                    "Medical identity theft",
                    "Insurance fraud",
                    "Discrimination based on health status",
                    "Privacy violations"
                ]
            ),
            "DATE_OF_BIRTH": PIITypeInfo(
                pii_type="DATE_OF_BIRTH",
                category="Personal Identifiers",
                description="Birth dates that can be used for identification and age verification",
                sensitivity_level="HIGH",
                common_examples=["1990-05-15", "DOB: 03/22/1985", "Born: December 1, 1978"],
                regulations=["GDPR", "CCPA", "HIPAA", "COPPA"],
                protection_requirements=[
                    "Age-appropriate consent mechanisms",
                    "Data minimization practices",
                    "Secure storage and transmission",
                    "Special protections for minors"
                ],
                risk_factors=[
                    "Identity verification bypass",
                    "Age discrimination",
                    "Social engineering",
                    "Cross-system correlation"
                ]
            ),
            "ADDRESS": PIITypeInfo(
                pii_type="ADDRESS",
                category="Location Information",
                description="Physical addresses including residential and business locations",
                sensitivity_level="MEDIUM",
                common_examples=["123 Main St, Anytown, ST 12345", "PO Box 789, City, State"],
                regulations=["GDPR", "CCPA", "HIPAA"],
                protection_requirements=[
                    "Consent for location-based services",
                    "Data minimization for service delivery",
                    "Secure geocoding and storage",
                    "Anonymous aggregation where possible"
                ],
                risk_factors=[
                    "Physical location tracking",
                    "Stalking and harassment",
                    "Burglary risk assessment",
                    "Demographic profiling"
                ]
            )
        }
    
    def generate_enhanced_report(self, session: HybridClassificationSession, 
                               field_analyses: List[EnhancedFieldAnalysis],
                               file_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive, user-friendly report with detailed explanations
        
        Args:
            session: Hybrid classification session with metadata
            field_analyses: List of enhanced field analysis results
            file_info: Optional file information for context
            
        Returns:
            Comprehensive report dictionary with detailed explanations
        """
        
        with comprehensive_logger.operation_context("generate_enhanced_report", "report_generator", 
                                                   session.session_id) as ctx:
            
            start_time = time.time()
            
            # Create comprehensive report structure
            report = {
                "report_id": str(uuid.uuid4()),
                "generated_at": datetime.now().isoformat(),
                "report_version": "2.0",
                "session_info": self._create_session_summary(session, file_info),
                "executive_summary": self._create_executive_summary(field_analyses, session),
                "findings_overview": self._create_findings_overview(field_analyses),
                "detailed_analysis": self._create_detailed_analysis(field_analyses),
                "regulation_compliance": self._create_regulation_compliance_analysis(field_analyses, session),
                "risk_assessment": self._create_risk_assessment(field_analyses),
                "recommendations": self._create_recommendations(field_analyses, session),
                "technical_details": self._create_technical_details(session, field_analyses),
                "appendices": self._create_appendices()
            }
            
            generation_time = (time.time() - start_time) * 1000
            report["metadata"] = {
                "generation_time_ms": generation_time,
                "total_fields_analyzed": len(field_analyses),
                "sensitive_fields_found": len([f for f in field_analyses if f.is_sensitive]),
                "regulations_analyzed": len(session.regulations),
                "confidence_threshold": 0.7  # Should come from session config
            }
            
            comprehensive_logger.info(f"Enhanced report generated successfully", 
                                    component="report_generator", operation="generate_enhanced_report",
                                    session_id=session.session_id, duration_ms=generation_time,
                                    metadata={"fields_analyzed": len(field_analyses)})
            
            return report
    
    def _create_session_summary(self, session: HybridClassificationSession, 
                               file_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create comprehensive session summary"""
        return {
            "session_id": session.session_id,
            "analysis_type": "PII/PHI Comprehensive Scan",
            "data_source": {
                "type": file_info.get("type", "unknown") if file_info else "unknown",
                "name": file_info.get("name", "N/A") if file_info else "N/A",
                "size": file_info.get("size", "N/A") if file_info else "N/A"
            },
            "scan_parameters": {
                "regulations": [reg.value if hasattr(reg, 'value') else str(reg) for reg in session.regulations],
                "total_fields": session.total_fields,
                "local_classifications": session.local_classifications,
                "ai_classifications": session.llm_classifications if hasattr(session, 'llm_classifications') else 0,
                "processing_time_seconds": round(session.total_processing_time, 2)
            },
            "quality_metrics": {
                "high_confidence_results": session.high_confidence_results,
                "low_confidence_results": session.low_confidence_results,
                "validation_errors": session.validation_errors,
                "cache_hits": session.cache_hits
            }
        }
    
    def _create_executive_summary(self, field_analyses: List[EnhancedFieldAnalysis], 
                                 session: HybridClassificationSession) -> Dict[str, Any]:
        """Create executive summary for business stakeholders"""
        sensitive_fields = [f for f in field_analyses if f.is_sensitive]
        critical_fields = [f for f in sensitive_fields if f.risk_level == RiskLevel.HIGH]
        
        risk_distribution = {}
        for field in sensitive_fields:
            risk_level = field.risk_level.value if hasattr(field.risk_level, 'value') else str(field.risk_level)
            risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
        
        return {
            "key_findings": [
                f"Analyzed {len(field_analyses)} data fields across your database schema",
                f"Identified {len(sensitive_fields)} fields containing sensitive personal information",
                f"Found {len(critical_fields)} high-risk fields requiring immediate attention",
                f"Compliance analysis completed for {len(session.regulations)} regulations"
            ],
            "risk_summary": {
                "overall_risk_level": self._calculate_overall_risk(field_analyses),
                "critical_issues": len(critical_fields),
                "total_sensitive_fields": len(sensitive_fields),
                "compliance_score": self._calculate_compliance_score(field_analyses),
                "risk_distribution": risk_distribution
            },
            "business_impact": {
                "regulatory_exposure": self._assess_regulatory_exposure(sensitive_fields),
                "data_protection_priority": "HIGH" if critical_fields else "MEDIUM",
                "estimated_compliance_effort": self._estimate_compliance_effort(sensitive_fields)
            },
            "immediate_actions": self._get_immediate_actions(critical_fields)
        }
    
    def _create_findings_overview(self, field_analyses: List[EnhancedFieldAnalysis]) -> Dict[str, Any]:
        """Create overview of all findings"""
        sensitive_fields = [f for f in field_analyses if f.is_sensitive]
        
        pii_type_counts = {}
        table_distribution = {}
        
        for field in sensitive_fields:
            pii_type = field.pii_type.value if hasattr(field.pii_type, 'value') else str(field.pii_type)
            pii_type_counts[pii_type] = pii_type_counts.get(pii_type, 0) + 1
            
            table_name = field.table_name or "unknown"
            if table_name not in table_distribution:
                table_distribution[table_name] = {"total": 0, "sensitive": 0}
            table_distribution[table_name]["sensitive"] += 1
        
        # Count total fields per table
        for field in field_analyses:
            table_name = field.table_name or "unknown"
            if table_name not in table_distribution:
                table_distribution[table_name] = {"total": 0, "sensitive": 0}
            table_distribution[table_name]["total"] += 1
        
        return {
            "summary": {
                "total_fields": len(field_analyses),
                "sensitive_fields": len(sensitive_fields),
                "non_sensitive_fields": len(field_analyses) - len(sensitive_fields),
                "sensitivity_percentage": round((len(sensitive_fields) / len(field_analyses)) * 100, 1) if field_analyses else 0
            },
            "pii_type_distribution": pii_type_counts,
            "table_analysis": table_distribution,
            "confidence_analysis": {
                "high_confidence": len([f for f in sensitive_fields if f.confidence_score >= 0.8]),
                "medium_confidence": len([f for f in sensitive_fields if 0.6 <= f.confidence_score < 0.8]),
                "low_confidence": len([f for f in sensitive_fields if f.confidence_score < 0.6])
            }
        }
    
    def _create_detailed_analysis(self, field_analyses: List[EnhancedFieldAnalysis]) -> List[Dict[str, Any]]:
        """Create detailed field-by-field analysis with explanations"""
        detailed_fields = []
        
        for field in field_analyses:
            if field.is_sensitive:
                pii_type_str = field.pii_type.value if hasattr(field.pii_type, 'value') else str(field.pii_type)
                risk_level_str = field.risk_level.value if hasattr(field.risk_level, 'value') else str(field.risk_level)
                
                field_detail = {
                    "field_name": field.field_name,
                    "table_name": field.table_name,
                    "classification": {
                        "pii_type": pii_type_str,
                        "risk_level": risk_level_str,
                        "confidence_score": round(field.confidence_score, 3),
                        "is_sensitive": field.is_sensitive
                    },
                    "why_sensitive": self._explain_why_sensitive(field),
                    "regulatory_impact": self._explain_regulatory_impact(field),
                    "protection_requirements": self._get_protection_requirements(field),
                    "risk_factors": self._get_risk_factors(field),
                    "recommendations": self._get_field_recommendations(field)
                }
                
                # Add PII type information if available
                if pii_type_str in self.pii_type_info:
                    pii_info = self.pii_type_info[pii_type_str]
                    field_detail["pii_type_details"] = {
                        "category": pii_info.category,
                        "description": pii_info.description,
                        "common_examples": pii_info.common_examples
                    }
                
                detailed_fields.append(field_detail)
        
        return sorted(detailed_fields, key=lambda x: (x["classification"]["risk_level"], x["field_name"]))
    
    def _explain_why_sensitive(self, field: EnhancedFieldAnalysis) -> str:
        """Explain why a field is considered sensitive"""
        pii_type_str = field.pii_type.value if hasattr(field.pii_type, 'value') else str(field.pii_type)
        
        explanations = {
            "EMAIL": f"The field '{field.field_name}' contains email addresses, which are direct personal identifiers that can be used to contact and identify individuals. Email addresses are considered personally identifiable information (PII) under multiple regulations.",
            
            "NAME": f"The field '{field.field_name}' contains personal names, which are direct identifiers of individuals. Names are fundamental PII that can be used alone or combined with other data to identify specific people.",
            
            "SSN": f"The field '{field.field_name}' contains Social Security Numbers, which are highly sensitive government-issued identifiers. SSNs pose significant identity theft risks and are strictly regulated.",
            
            "PHONE": f"The field '{field.field_name}' contains telephone numbers, which are personal contact information that can be used to identify and communicate with individuals. Phone numbers are regulated PII, especially for marketing communications.",
            
            "FINANCIAL": f"The field '{field.field_name}' contains financial information such as credit card or account numbers. This is highly sensitive data that poses fraud and financial theft risks.",
            
            "MEDICAL_ID": f"The field '{field.field_name}' contains medical or patient identifiers. This is Protected Health Information (PHI) under HIPAA and requires strict handling and access controls.",
            
            "DATE_OF_BIRTH": f"The field '{field.field_name}' contains birth dates, which are personal identifiers often used for verification and can be combined with other data for identity theft.",
            
            "ADDRESS": f"The field '{field.field_name}' contains physical addresses, which are location-based personal information that can identify where individuals live or work."
        }
        
        return explanations.get(pii_type_str, 
                               f"The field '{field.field_name}' has been classified as {pii_type_str} with {round(field.confidence_score * 100)}% confidence based on pattern analysis and regulatory definitions.")
    
    def _explain_regulatory_impact(self, field: EnhancedFieldAnalysis) -> List[Dict[str, str]]:
        """Explain which regulations apply and why"""
        pii_type_str = field.pii_type.value if hasattr(field.pii_type, 'value') else str(field.pii_type)
        regulatory_impact = []
        
        # Map PII types to relevant regulations
        regulation_mappings = {
            "EMAIL": ["GDPR", "CCPA"],
            "NAME": ["GDPR", "CCPA", "HIPAA"],
            "SSN": ["HIPAA", "CCPA", "SOX"],
            "PHONE": ["GDPR", "CCPA", "TCPA"],
            "FINANCIAL": ["PCI-DSS", "GLBA", "GDPR", "CCPA"],
            "MEDICAL_ID": ["HIPAA", "HITECH", "GDPR"],
            "DATE_OF_BIRTH": ["GDPR", "CCPA", "HIPAA", "COPPA"],
            "ADDRESS": ["GDPR", "CCPA", "HIPAA"]
        }
        
        applicable_regulations = regulation_mappings.get(pii_type_str, [])
        
        for reg in applicable_regulations:
            if reg in self.regulation_info:
                reg_info = self.regulation_info[reg]
                regulatory_impact.append({
                    "regulation": reg_info.name,
                    "full_name": reg_info.full_name,
                    "why_applicable": f"This {pii_type_str} data type is covered under {reg_info.name} because {reg_info.description.split('.')[0].lower()}.",
                    "key_requirements": reg_info.key_requirements[:3],  # Top 3 requirements
                    "penalties": reg_info.penalties
                })
        
        return regulatory_impact
    
    def _get_protection_requirements(self, field: EnhancedFieldAnalysis) -> List[str]:
        """Get specific protection requirements for the field"""
        pii_type_str = field.pii_type.value if hasattr(field.pii_type, 'value') else str(field.pii_type)
        
        if pii_type_str in self.pii_type_info:
            return self.pii_type_info[pii_type_str].protection_requirements
        
        # Default protection requirements
        return [
            "Implement access controls and authentication",
            "Encrypt data in transit and at rest",
            "Maintain audit logs of access and changes",
            "Apply data minimization principles"
        ]
    
    def _get_risk_factors(self, field: EnhancedFieldAnalysis) -> List[str]:
        """Get specific risk factors for the field"""
        pii_type_str = field.pii_type.value if hasattr(field.pii_type, 'value') else str(field.pii_type)
        
        if pii_type_str in self.pii_type_info:
            return self.pii_type_info[pii_type_str].risk_factors
        
        # Default risk factors
        return [
            "Unauthorized access and data breaches",
            "Identity theft and privacy violations",
            "Regulatory non-compliance and penalties",
            "Reputational damage and loss of trust"
        ]
    
    def _get_field_recommendations(self, field: EnhancedFieldAnalysis) -> List[str]:
        """Get specific recommendations for the field"""
        pii_type_str = field.pii_type.value if hasattr(field.pii_type, 'value') else str(field.pii_type)
        risk_level_str = field.risk_level.value if hasattr(field.risk_level, 'value') else str(field.risk_level)
        
        recommendations = []
        
        # Risk-level specific recommendations
        if risk_level_str == "HIGH":
            recommendations.extend([
                "Implement strongest available encryption (AES-256)",
                "Require multi-factor authentication for access",
                "Conduct regular security audits and penetration testing",
                "Implement real-time monitoring and alerting"
            ])
        elif risk_level_str == "MEDIUM":
            recommendations.extend([
                "Apply standard encryption and access controls",
                "Implement role-based access restrictions",
                "Regular access reviews and compliance checks"
            ])
        else:
            recommendations.extend([
                "Apply basic security controls and monitoring",
                "Include in regular data governance reviews"
            ])
        
        # PII type specific recommendations
        if pii_type_str == "SSN":
            recommendations.append("Consider tokenization or masking for non-essential uses")
        elif pii_type_str == "EMAIL":
            recommendations.append("Implement consent management for marketing communications")
        elif pii_type_str == "MEDICAL_ID":
            recommendations.append("Ensure HIPAA-compliant access controls and audit trails")
        elif pii_type_str == "FINANCIAL":
            recommendations.append("Implement PCI-DSS compliance requirements")
        
        return recommendations
    
    def _create_regulation_compliance_analysis(self, field_analyses: List[EnhancedFieldAnalysis], 
                                             session: HybridClassificationSession) -> Dict[str, Any]:
        """Create detailed regulation compliance analysis"""
        sensitive_fields = [f for f in field_analyses if f.is_sensitive]
        compliance_analysis = {}
        
        for regulation in session.regulations:
            reg_name = regulation.value if hasattr(regulation, 'value') else str(regulation)
            
            # Count fields affected by this regulation
            affected_fields = []
            for field in sensitive_fields:
                pii_type_str = field.pii_type.value if hasattr(field.pii_type, 'value') else str(field.pii_type)
                if reg_name in self.pii_type_info.get(pii_type_str, PIITypeInfo("", "", "", "", [], [], [], [])).regulations:
                    affected_fields.append(field)
            
            if reg_name in self.regulation_info:
                reg_info = self.regulation_info[reg_name]
                compliance_analysis[reg_name] = {
                    "regulation_overview": {
                        "full_name": reg_info.full_name,
                        "description": reg_info.description,
                        "scope": reg_info.scope,
                        "penalties": reg_info.penalties
                    },
                    "compliance_status": {
                        "affected_fields": len(affected_fields),
                        "high_risk_fields": len([f for f in affected_fields if f.risk_level == RiskLevel.HIGH]),
                        "compliance_score": self._calculate_regulation_compliance_score(affected_fields),
                        "priority_level": "HIGH" if len(affected_fields) > 5 else "MEDIUM" if len(affected_fields) > 0 else "LOW"
                    },
                    "key_requirements": reg_info.key_requirements,
                    "affected_field_details": [
                        {
                            "field_name": f.field_name,
                            "table_name": f.table_name,
                            "pii_type": f.pii_type.value if hasattr(f.pii_type, 'value') else str(f.pii_type),
                            "risk_level": f.risk_level.value if hasattr(f.risk_level, 'value') else str(f.risk_level),
                            "confidence": round(f.confidence_score, 3)
                        } for f in affected_fields[:10]  # Limit to first 10 for readability
                    ]
                }
        
        return compliance_analysis
    
    def _create_risk_assessment(self, field_analyses: List[EnhancedFieldAnalysis]) -> Dict[str, Any]:
        """Create comprehensive risk assessment"""
        sensitive_fields = [f for f in field_analyses if f.is_sensitive]
        
        risk_by_level = {"HIGH": [], "MEDIUM": [], "LOW": []}
        for field in sensitive_fields:
            risk_level = field.risk_level.value if hasattr(field.risk_level, 'value') else str(field.risk_level)
            risk_by_level[risk_level].append(field)
        
        return {
            "overall_risk_score": self._calculate_overall_risk_score(field_analyses),
            "risk_distribution": {
                "high_risk": len(risk_by_level["HIGH"]),
                "medium_risk": len(risk_by_level["MEDIUM"]),
                "low_risk": len(risk_by_level["LOW"])
            },
            "primary_risk_factors": self._identify_primary_risks(sensitive_fields),
            "threat_vectors": self._identify_threat_vectors(sensitive_fields),
            "business_impact_assessment": self._assess_business_impact(sensitive_fields)
        }
    
    def _create_recommendations(self, field_analyses: List[EnhancedFieldAnalysis], 
                              session: HybridClassificationSession) -> Dict[str, List[str]]:
        """Create actionable recommendations"""
        sensitive_fields = [f for f in field_analyses if f.is_sensitive]
        
        return {
            "immediate_actions": [
                "Review and secure all HIGH risk fields identified in this report",
                "Implement access controls and encryption for sensitive data fields",
                "Conduct security training for personnel with access to sensitive data",
                "Establish incident response procedures for data breaches"
            ],
            "short_term_improvements": [
                "Implement comprehensive data governance policies",
                "Deploy data loss prevention (DLP) solutions",
                "Establish regular compliance auditing procedures",
                "Create data retention and disposal policies"
            ],
            "long_term_strategic_actions": [
                "Develop privacy-by-design architecture principles",
                "Implement automated compliance monitoring",
                "Establish privacy impact assessment procedures",
                "Create comprehensive staff privacy training programs"
            ],
            "regulatory_compliance_steps": [
                f"Ensure compliance with {len(session.regulations)} applicable regulations",
                "Implement required consent mechanisms",
                "Establish data subject rights procedures",
                "Create breach notification procedures"
            ]
        }
    
    def _create_technical_details(self, session: HybridClassificationSession, 
                                 field_analyses: List[EnhancedFieldAnalysis]) -> Dict[str, Any]:
        """Create technical details for IT and compliance teams"""
        return {
            "analysis_methodology": {
                "local_pattern_matching": f"{session.local_classifications} fields analyzed using regulatory patterns",
                "ai_classification": f"{getattr(session, 'llm_classifications', 0)} fields analyzed using AI models",
                "confidence_threshold": "0.7 (70%)",
                "processing_approach": "Hybrid local-first with AI fallback for edge cases"
            },
            "performance_metrics": {
                "total_processing_time": f"{round(session.total_processing_time, 2)} seconds",
                "average_field_processing_time": f"{round(session.total_processing_time / session.total_fields * 1000, 2)} ms per field" if session.total_fields > 0 else "N/A",
                "cache_hit_rate": f"{round((session.cache_hits / session.total_fields) * 100, 1)}%" if session.total_fields > 0 else "N/A",
                "high_confidence_rate": f"{round((session.high_confidence_results / session.total_fields) * 100, 1)}%" if session.total_fields > 0 else "N/A"
            },
            "quality_indicators": {
                "validation_errors": session.validation_errors,
                "low_confidence_results": session.low_confidence_results,
                "manual_review_required": len([f for f in field_analyses if f.confidence_score < 0.7])
            },
            "field_classification_summary": {
                field.field_name: {
                    "pii_type": field.pii_type.value if hasattr(field.pii_type, 'value') else str(field.pii_type),
                    "confidence": round(field.confidence_score, 3),
                    "risk_level": field.risk_level.value if hasattr(field.risk_level, 'value') else str(field.risk_level),
                    "detection_method": field.detection_method.value if hasattr(field.detection_method, 'value') else str(field.detection_method)
                } for field in field_analyses if field.is_sensitive
            }
        }
    
    def _create_appendices(self) -> Dict[str, Any]:
        """Create appendices with reference information"""
        return {
            "regulation_reference": {
                reg_name: {
                    "full_name": reg_info.full_name,
                    "description": reg_info.description,
                    "key_requirements": reg_info.key_requirements,
                    "penalties": reg_info.penalties,
                    "scope": reg_info.scope
                } for reg_name, reg_info in self.regulation_info.items()
            },
            "pii_type_reference": {
                pii_type: {
                    "category": info.category,
                    "description": info.description,
                    "sensitivity_level": info.sensitivity_level,
                    "common_examples": info.common_examples,
                    "regulations": info.regulations
                } for pii_type, info in self.pii_type_info.items()
            },
            "glossary": {
                "PII": "Personally Identifiable Information - any data that could potentially be used to identify a particular person",
                "PHI": "Protected Health Information - individually identifiable health information held or transmitted by covered entities or business associates",
                "Data Subject": "An identified or identifiable natural person whose personal data is processed",
                "Data Controller": "The entity that determines the purposes and means of processing personal data",
                "Data Processor": "An entity that processes personal data on behalf of the data controller"
            }
        }
    
    # Helper methods for calculations
    def _calculate_overall_risk(self, field_analyses: List[EnhancedFieldAnalysis]) -> str:
        """Calculate overall risk level"""
        sensitive_fields = [f for f in field_analyses if f.is_sensitive]
        if not sensitive_fields:
            return "LOW"
        
        high_risk_count = len([f for f in sensitive_fields if f.risk_level == RiskLevel.HIGH])
        if high_risk_count > 5:
            return "CRITICAL"
        elif high_risk_count > 0:
            return "HIGH"
        elif len(sensitive_fields) > 10:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_compliance_score(self, field_analyses: List[EnhancedFieldAnalysis]) -> int:
        """Calculate overall compliance score (0-100)"""
        if not field_analyses:
            return 100
        
        sensitive_fields = [f for f in field_analyses if f.is_sensitive]
        if not sensitive_fields:
            return 100
        
        # Base score calculation
        total_score = 0
        for field in sensitive_fields:
            if field.risk_level == RiskLevel.HIGH:
                total_score += max(0, 100 - 30)  # High risk reduces score significantly
            elif field.risk_level == RiskLevel.MEDIUM:
                total_score += max(0, 100 - 15)  # Medium risk moderate impact
            else:
                total_score += max(0, 100 - 5)   # Low risk minimal impact
        
        average_score = total_score / len(sensitive_fields) if sensitive_fields else 100
        return max(0, min(100, int(average_score)))
    
    def _calculate_overall_risk_score(self, field_analyses: List[EnhancedFieldAnalysis]) -> float:
        """Calculate numerical risk score (0.0-10.0)"""
        sensitive_fields = [f for f in field_analyses if f.is_sensitive]
        if not sensitive_fields:
            return 0.0
        
        risk_score = 0.0
        for field in sensitive_fields:
            if field.risk_level == RiskLevel.HIGH:
                risk_score += 3.0
            elif field.risk_level == RiskLevel.MEDIUM:
                risk_score += 2.0
            else:
                risk_score += 1.0
        
        # Normalize to 0-10 scale
        max_possible_score = len(sensitive_fields) * 3.0
        normalized_score = (risk_score / max_possible_score) * 10.0 if max_possible_score > 0 else 0.0
        
        return min(10.0, normalized_score)
    
    def _calculate_regulation_compliance_score(self, affected_fields: List[EnhancedFieldAnalysis]) -> int:
        """Calculate compliance score for specific regulation"""
        if not affected_fields:
            return 100
        
        high_risk_count = len([f for f in affected_fields if f.risk_level == RiskLevel.HIGH])
        medium_risk_count = len([f for f in affected_fields if f.risk_level == RiskLevel.MEDIUM])
        
        # Compliance score calculation
        score = 100 - (high_risk_count * 20) - (medium_risk_count * 10)
        return max(0, min(100, score))
    
    def _assess_regulatory_exposure(self, sensitive_fields: List[EnhancedFieldAnalysis]) -> List[str]:
        """Assess regulatory exposure based on sensitive fields"""
        exposures = []
        
        if any(f.pii_type in [PIIType.SSN, PIIType.MEDICAL_ID] for f in sensitive_fields):
            exposures.append("HIGH - Healthcare and financial data present")
        
        if len(sensitive_fields) > 20:
            exposures.append("HIGH - Large volume of sensitive data")
        elif len(sensitive_fields) > 10:
            exposures.append("MEDIUM - Moderate volume of sensitive data")
        
        if any(f.risk_level == RiskLevel.HIGH for f in sensitive_fields):
            exposures.append("HIGH - Critical risk fields identified")
        
        return exposures if exposures else ["LOW - Limited regulatory exposure"]
    
    def _estimate_compliance_effort(self, sensitive_fields: List[EnhancedFieldAnalysis]) -> str:
        """Estimate compliance implementation effort"""
        high_risk_count = len([f for f in sensitive_fields if f.risk_level == RiskLevel.HIGH])
        
        if high_risk_count > 10:
            return "HIGH - Significant compliance implementation required (6-12 months)"
        elif high_risk_count > 5:
            return "MEDIUM - Moderate compliance work needed (3-6 months)"
        elif len(sensitive_fields) > 0:
            return "LOW - Basic compliance measures sufficient (1-3 months)"
        else:
            return "MINIMAL - Limited compliance requirements"
    
    def _get_immediate_actions(self, critical_fields: List[EnhancedFieldAnalysis]) -> List[str]:
        """Get immediate actions needed for critical fields"""
        if not critical_fields:
            return ["Continue monitoring and maintain current security practices"]
        
        actions = [
            f"Secure {len(critical_fields)} high-risk fields immediately",
            "Implement access controls and encryption",
            "Conduct security audit of affected systems",
            "Review and update data handling procedures"
        ]
        
        return actions
    
    def _identify_primary_risks(self, sensitive_fields: List[EnhancedFieldAnalysis]) -> List[str]:
        """Identify primary risk factors"""
        risks = set()
        
        for field in sensitive_fields:
            pii_type_str = field.pii_type.value if hasattr(field.pii_type, 'value') else str(field.pii_type)
            if pii_type_str in self.pii_type_info:
                risks.update(self.pii_type_info[pii_type_str].risk_factors[:2])  # Top 2 risks per type
        
        return list(risks)
    
    def _identify_threat_vectors(self, sensitive_fields: List[EnhancedFieldAnalysis]) -> List[str]:
        """Identify potential threat vectors"""
        threats = []
        
        if any(f.pii_type == PIIType.SSN for f in sensitive_fields):
            threats.append("Identity theft through Social Security Number exposure")
        
        if any(f.pii_type == PIIType.FINANCIAL for f in sensitive_fields):
            threats.append("Financial fraud through payment card data exposure")
        
        if any(f.pii_type == PIIType.EMAIL for f in sensitive_fields):
            threats.append("Phishing and social engineering attacks")
        
        if any(f.pii_type == PIIType.MEDICAL_ID for f in sensitive_fields):
            threats.append("Medical identity theft and insurance fraud")
        
        return threats if threats else ["General data privacy violations"]
    
    def _assess_business_impact(self, sensitive_fields: List[EnhancedFieldAnalysis]) -> Dict[str, str]:
        """Assess business impact of identified risks"""
        high_risk_count = len([f for f in sensitive_fields if f.risk_level == RiskLevel.HIGH])
        
        impact_levels = {
            "financial_impact": "HIGH" if high_risk_count > 5 else "MEDIUM" if high_risk_count > 0 else "LOW",
            "reputational_impact": "HIGH" if high_risk_count > 10 else "MEDIUM" if len(sensitive_fields) > 5 else "LOW",
            "operational_impact": "HIGH" if len(sensitive_fields) > 20 else "MEDIUM" if len(sensitive_fields) > 10 else "LOW",
            "regulatory_impact": "HIGH" if high_risk_count > 3 else "MEDIUM" if len(sensitive_fields) > 5 else "LOW"
        }
        
        return impact_levels

# Global instance
enhanced_report_generator = EnhancedReportGenerator()