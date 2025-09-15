"""
Regulatory Pattern Loader
Loads and processes regulatory field patterns from CSV files to create comprehensive 
pattern databases for maximum accuracy PII/PHI detection
"""

import csv
import re
import hashlib
from typing import Dict, List, Set, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
import json

from pii_scanner_poc.models.data_models import PIIType, RiskLevel, Regulation
from pii_scanner_poc.models.enhanced_data_models import SensitivityPattern, calculate_confidence_level
from pii_scanner_poc.utils.logging_config import main_logger


def _get_data_file_path(filename: str) -> str:
    """Get the correct path to data files, working cross-platform"""
    # First try relative to current directory (for local development)
    current_dir_path = Path(filename)
    if current_dir_path.exists():
        return str(current_dir_path)
    
    # Try in the app root directory
    app_root_path = Path(__file__).parent.parent.parent / filename
    if app_root_path.exists():
        return str(app_root_path)
    
    # Try the hardcoded /app/ path (for Linux containers)
    linux_path = Path(f"/app/{filename}")
    if linux_path.exists():
        return str(linux_path)
    
    # Fallback to relative path
    return filename


@dataclass
class RegulatoryField:
    """Represents a regulatory field definition"""
    field_name: str
    aliases: List[str]
    pii_type: PIIType
    risk_level: RiskLevel
    regulations: List[Regulation]
    category: str
    confidence: float
    description: str = ""
    examples: List[str] = None
    sub_fields: List[str] = None


class RegulatoryPatternLoader:
    """Loads regulatory patterns from CSV files and creates comprehensive pattern databases"""
    
    def __init__(self):
        self.regulatory_fields: Dict[str, RegulatoryField] = {}
        self.alias_mappings: Dict[str, str] = {}
        self.pattern_cache: Dict[str, SensitivityPattern] = {}
        self.loaded_files: Set[str] = set()
        
        main_logger.info("Regulatory pattern loader initialized", extra={
            'component': 'regulatory_loader'
        })
    
    def load_hipaa_patterns(self, file_path: str = None) -> Dict[str, List[SensitivityPattern]]:
        """Load HIPAA PII/PHI field patterns from CSV"""
        if file_path is None:
            file_path = _get_data_file_path("hipaa_fields.csv")
            
        try:
            patterns = {}
            
            # Read HIPAA CSV with latin-1 encoding, skipping empty first line
            with open(file_path, 'r', encoding='latin-1') as f:
                lines = f.readlines()
                
                # Find the actual header line (skip empty lines)
                header_line_idx = 0
                for i, line in enumerate(lines):
                    if line.strip() and 'Attribute Name' in line:
                        header_line_idx = i
                        break
                
                # Create reader starting from header line
                from io import StringIO
                csv_content = ''.join(lines[header_line_idx:])
                reader = csv.DictReader(StringIO(csv_content))
                
                row_count = 0
                for row in reader:
                    row_count += 1
                    
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    
                    # Extract field information
                    field_name = row.get('Attribute Name', '').strip()
                    if not field_name:
                        continue
                    
                    field_type = row.get('Type of Field', '').strip()
                    aliases = row.get('Alias Names', '').strip()
                    examples = row.get('Examples', '').strip()
                    comments = row.get('Comments', '').strip()
                    sub_fields = row.get('Sub-fields', '').strip()
                    
                    # Determine PII type
                    pii_type = self._map_hipaa_field_to_pii_type(field_name, field_type, comments)
                    
                    # Determine risk level - HIPAA fields are generally HIGH risk
                    risk_level = RiskLevel.HIGH if 'PHI' in field_type else RiskLevel.HIGH
                    
                    # Process aliases
                    alias_list = self._process_aliases(aliases, sub_fields, examples)
                    alias_list.append(field_name.lower())
                    
                    # Create regulatory field
                    reg_field = RegulatoryField(
                        field_name=field_name,
                        aliases=list(set(alias_list)),  # Remove duplicates
                        pii_type=pii_type,
                        risk_level=risk_level,
                        regulations=[Regulation.HIPAA],
                        category="HIPAA",
                        confidence=0.95,  # High confidence for HIPAA patterns
                        description=comments,
                        examples=self._process_examples(examples),
                        sub_fields=self._process_sub_fields(sub_fields)
                    )
                    
                    self.regulatory_fields[field_name.lower()] = reg_field
                    
                    # Create sensitivity patterns
                    field_patterns = self._create_sensitivity_patterns(reg_field)
                    patterns[field_name.lower()] = field_patterns
            
            main_logger.info(f"Loaded {len(patterns)} HIPAA field patterns from {row_count} rows", extra={
                'component': 'regulatory_loader',
                'file': file_path,
                'pattern_count': len(patterns),
                'rows_processed': row_count
            })
            
            return patterns
            
        except Exception as e:
            main_logger.error(f"Error loading HIPAA patterns: {e}", extra={
                'component': 'regulatory_loader',
                'file': file_path,
                'error': str(e)
            })
            return {}
    
    def load_gdpr_patterns(self, file_path: str = None) -> Dict[str, List[SensitivityPattern]]:
        """Load GDPR PII field patterns from CSV"""
        if file_path is None:
            file_path = _get_data_file_path("gdpr_fields.csv")
            
        try:
            patterns = {}
            
            # Read GDPR CSV with latin-1 encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                reader = csv.DictReader(f)
                
                row_count = 0
                for row in reader:
                    row_count += 1
                    
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    
                    # Extract field information - handle different possible column names
                    field_name = (row.get('Attribute name/PII fields ') or 
                                row.get('Attribute name/PII fields') or 
                                row.get('attribute_name_pii_fields') or 
                                row.get('Attribute name') or '').strip()
                    
                    if not field_name:
                        continue
                    
                    aliases = (row.get('Aliases (Database columns)') or 
                             row.get('aliases_database_columns') or 
                             row.get('Aliases') or '').strip()
                    field_type = (row.get('Type of field') or 
                                row.get('type_of_field') or 
                                row.get('Type') or '').strip()
                    comments = (row.get('Comments') or row.get('comments') or '').strip()
                    
                    # Determine PII type
                    pii_type = self._map_gdpr_field_to_pii_type(field_name, field_type, comments)
                    
                    # Determine risk level
                    risk_level = self._determine_gdpr_risk_level(field_name, field_type)
                    
                    # Process aliases
                    alias_list = self._process_aliases(aliases, "", "")
                    alias_list.append(field_name.lower())
                    
                    # Create regulatory field
                    reg_field = RegulatoryField(
                        field_name=field_name,
                        aliases=list(set(alias_list)),  # Remove duplicates
                        pii_type=pii_type,
                        risk_level=risk_level,
                        regulations=[Regulation.GDPR],
                        category="GDPR",
                        confidence=0.92,  # High confidence for GDPR patterns
                        description=comments
                    )
                    
                    self.regulatory_fields[field_name.lower()] = reg_field
                    
                    # Create sensitivity patterns
                    field_patterns = self._create_sensitivity_patterns(reg_field)
                    patterns[field_name.lower()] = field_patterns
            
            main_logger.info(f"Loaded {len(patterns)} GDPR field patterns from {row_count} rows", extra={
                'component': 'regulatory_loader',
                'file': file_path,
                'pattern_count': len(patterns),
                'rows_processed': row_count
            })
            
            return patterns
            
        except Exception as e:
            main_logger.error(f"Error loading GDPR patterns: {e}", extra={
                'component': 'regulatory_loader',
                'file': file_path,
                'error': str(e)
            })
            return {}
    
    def load_alias_patterns(self, file_path: str = None) -> Dict[str, str]:
        """Load attribute alias mappings from CSV"""
        if file_path is None:
            file_path = _get_data_file_path("attribute_alias.csv")
            
        try:
            alias_mappings = {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Process PII aliases
                    pii_alias = row.get('PII Alias List', '').strip()
                    if pii_alias:
                        alias_mappings[pii_alias.lower()] = 'PII'
                    
                    # Process GDPR aliases
                    gdpr_alias = row.get('GDPR Alias List', '').strip()
                    if gdpr_alias:
                        alias_mappings[gdpr_alias.lower()] = 'GDPR'
                    
                    # Process HIPAA aliases
                    hipaa_alias = row.get('HIPAA Alias List', '').strip()
                    if hipaa_alias:
                        alias_mappings[hipaa_alias.lower()] = 'HIPAA'
            
            self.alias_mappings.update(alias_mappings)
            
            main_logger.info(f"Loaded {len(alias_mappings)} alias mappings", extra={
                'component': 'regulatory_loader',
                'file': file_path,
                'alias_count': len(alias_mappings)
            })
            
            return alias_mappings
            
        except Exception as e:
            main_logger.error(f"Error loading alias patterns: {e}", extra={
                'component': 'regulatory_loader',
                'file': file_path,
                'error': str(e)
            })
            return {}
    
    def _map_hipaa_field_to_pii_type(self, field_name: str, field_type: str, comments: str) -> PIIType:
        """Map HIPAA field to PII type"""
        field_lower = field_name.lower()
        type_lower = field_type.lower()
        comments_lower = comments.lower()
        
        # Medical/Health information
        if any(term in field_lower + type_lower + comments_lower for term in [
            'medical', 'diagnosis', 'prescription', 'treatment', 'patient', 'clinical',
            'health', 'procedure', 'hospital', 'physician', 'lab', 'test'
        ]):
            return PIIType.MEDICAL
        
        # Names
        if any(term in field_lower for term in ['name', 'first', 'last', 'given', 'surname']):
            return PIIType.NAME
        
        # Contact information
        if any(term in field_lower for term in ['phone', 'telephone', 'mobile', 'cell']):
            return PIIType.PHONE
        
        if any(term in field_lower for term in ['email', 'mail']):
            return PIIType.EMAIL
        
        # Address information
        if any(term in field_lower for term in ['address', 'street', 'city', 'state', 'zip']):
            return PIIType.ADDRESS
        
        # IDs and numbers
        if any(term in field_lower for term in ['ssn', 'social', 'id', 'number', 'mrn', 'medical_record']):
            return PIIType.ID
        
        # Financial
        if any(term in field_lower for term in ['account', 'insurance', 'payment', 'billing']):
            return PIIType.FINANCIAL
        
        # Biometric
        if any(term in field_lower for term in ['fingerprint', 'biometric', 'photo', 'image']):
            return PIIType.BIOMETRIC
        
        return PIIType.OTHER
    
    def _map_gdpr_field_to_pii_type(self, field_name: str, field_type: str, comments: str) -> PIIType:
        """Map GDPR field to PII type"""
        field_lower = field_name.lower()
        type_lower = field_type.lower()
        
        # Names
        if any(term in field_lower for term in ['name', 'first', 'last', 'surname']):
            return PIIType.NAME
        
        # Contact information
        if any(term in field_lower for term in ['phone', 'telephone', 'mobile']):
            return PIIType.PHONE
        
        if any(term in field_lower for term in ['email', 'mail']):
            return PIIType.EMAIL
        
        # Address
        if any(term in field_lower for term in ['address', 'street', 'city', 'postal']):
            return PIIType.ADDRESS
        
        # Financial
        if any(term in field_lower for term in ['credit', 'card', 'account', 'bank', 'payment']):
            return PIIType.FINANCIAL
        
        # IDs
        if any(term in field_lower for term in ['id', 'ssn', 'social', 'national']):
            return PIIType.ID
        
        # Network
        if any(term in field_lower for term in ['ip', 'cookie', 'session']):
            return PIIType.NETWORK
        
        # Biometric
        if any(term in field_lower for term in ['photo', 'image', 'biometric', 'fingerprint']):
            return PIIType.BIOMETRIC
        
        return PIIType.OTHER
    
    def _determine_gdpr_risk_level(self, field_name: str, field_type: str) -> RiskLevel:
        """Determine GDPR risk level"""
        field_lower = field_name.lower()
        type_lower = field_type.lower()
        
        # High risk categories
        high_risk_terms = ['name', 'email', 'phone', 'address', 'ssn', 'credit', 'card', 'biometric']
        if any(term in field_lower for term in high_risk_terms):
            return RiskLevel.HIGH
        
        # Medium risk categories
        medium_risk_terms = ['id', 'ip', 'cookie', 'session', 'location']
        if any(term in field_lower for term in medium_risk_terms):
            return RiskLevel.MEDIUM
        
        return RiskLevel.LOW
    
    def _process_aliases(self, aliases: str, sub_fields: str = "", examples: str = "") -> List[str]:
        """Enhanced alias processing to handle complex patterns from CSV data"""
        alias_list = []
        
        # Process main aliases with enhanced parsing
        if aliases:
            # Split by multiple common delimiters
            for delimiter in [',', ';', '\n', '|', '/', '\\']:
                if delimiter in aliases:
                    alias_parts = aliases.split(delimiter)
                    break
            else:
                alias_parts = [aliases]
            
            for alias in alias_parts:
                cleaned_alias = self._clean_field_name(alias.strip())
                if cleaned_alias:
                    alias_list.append(cleaned_alias)
                    
                    # Generate common variations of the alias
                    variations = self._generate_alias_variations(cleaned_alias)
                    alias_list.extend(variations)
        
        # Process sub-fields with enhanced parsing
        if sub_fields:
            for delimiter in [',', ';', '\n', '|', '/', '\\']:
                if delimiter in sub_fields:
                    sub_parts = sub_fields.split(delimiter)
                    break
            else:
                sub_parts = [sub_fields]
            
            for sub_field in sub_parts:
                cleaned_sub = self._clean_field_name(sub_field.strip())
                if cleaned_sub:
                    alias_list.append(cleaned_sub)
                    
                    # Generate variations
                    variations = self._generate_alias_variations(cleaned_sub)
                    alias_list.extend(variations)
        
        # Process examples for additional patterns
        if examples:
            # Extract field-like patterns from examples
            example_patterns = self._extract_field_patterns_from_examples(examples)
            alias_list.extend(example_patterns)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_aliases = []
        for alias in alias_list:
            if alias and alias not in seen:
                seen.add(alias)
                unique_aliases.append(alias)
        
        return unique_aliases
    
    def _generate_alias_variations(self, alias: str) -> List[str]:
        """Generate common variations of an alias for better matching"""
        variations = []
        
        # Basic transformations
        variations.extend([
            alias.replace('_', ''),          # Remove underscores
            alias.replace('_', ' '),         # Underscore to space
            alias.replace(' ', '_'),         # Space to underscore
            alias.replace('-', '_'),         # Dash to underscore
            alias.replace('-', ''),          # Remove dashes
        ])
        
        # Add common prefixes that might be found in actual schemas
        prefixes = ['user_', 'customer_', 'client_', 'person_', 'member_', 'patient_', 'primary_', 'secondary_']
        for prefix in prefixes:
            variations.append(f"{prefix}{alias}")
            variations.append(f"{prefix}{alias.replace('_', '')}")
        
        # Add common suffixes
        suffixes = ['_id', '_no', '_num', '_number', '_code', '_info', '_data', '_addr', '_contact']
        for suffix in suffixes:
            variations.append(f"{alias}{suffix}")
        
        # Handle specific common patterns from user's DDL
        if 'name' in alias.lower():
            variations.extend([
                f"cust_{alias}",
                f"usr_{alias}",
                f"client_{alias}",
                f"member_{alias}",
                alias.replace('name', 'nm'),
                alias.replace('_name', '_nm')
            ])
        
        if 'email' in alias.lower():
            variations.extend([
                f"primary_{alias}_addr",
                f"work_{alias}_id",
                f"personal_{alias}_contact",
                f"backup_{alias}_info",
                alias.replace('email', 'mail')
            ])
        
        if 'phone' in alias.lower():
            variations.extend([
                f"primary_{alias}_no",
                f"home_telephone_number",
                f"mobile_{alias}_contact",
                f"cell_{alias}_info",
                f"emergency_{alias}_contact"
            ])
        
        # Remove empty and duplicate variations
        return [v for v in variations if v and v != alias]
    
    def _extract_field_patterns_from_examples(self, examples: str) -> List[str]:
        """Extract potential field name patterns from examples"""
        patterns = []
        
        # Look for patterns that might be field names in the examples
        import re
        
        # Extract words that look like field names (contain underscores, alphanumeric)
        field_like_patterns = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]+\b', examples)
        
        for pattern in field_like_patterns:
            # Clean and add if it looks like a field name
            if '_' in pattern or pattern.islower():
                cleaned = self._clean_field_name(pattern)
                if cleaned and len(cleaned) > 2:
                    patterns.append(cleaned)
        
        return patterns
    
    def _process_examples(self, examples: str) -> List[str]:
        """Process examples from CSV"""
        if not examples:
            return []
        
        example_list = []
        for delimiter in [',', ';', '\n']:
            if delimiter in examples:
                example_parts = examples.split(delimiter)
                break
        else:
            example_parts = [examples]
        
        for example in example_parts:
            cleaned = example.strip()
            if cleaned and len(cleaned) < 100:  # Reasonable length limit
                example_list.append(cleaned)
        
        return example_list[:5]  # Limit to 5 examples
    
    def _process_sub_fields(self, sub_fields: str) -> List[str]:
        """Process sub-fields from CSV"""
        if not sub_fields:
            return []
        
        sub_list = []
        for delimiter in [',', ';', '\n']:
            if delimiter in sub_fields:
                sub_parts = sub_fields.split(delimiter)
                break
        else:
            sub_parts = [sub_fields]
        
        for sub_field in sub_parts:
            cleaned = self._clean_field_name(sub_field.strip())
            if cleaned:
                sub_list.append(cleaned)
        
        return sub_list
    
    def _clean_field_name(self, field_name: str) -> str:
        """Clean and normalize field names"""
        if not field_name:
            return ""
        
        # Remove special characters and extra whitespace
        cleaned = re.sub(r'[^\w\s_-]', '', field_name.strip())
        cleaned = re.sub(r'\s+', '_', cleaned)
        cleaned = cleaned.lower()
        
        # Remove common prefixes/suffixes that aren't meaningful
        prefixes_to_remove = ['the_', 'a_', 'an_']
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):]
        
        return cleaned if len(cleaned) > 1 else ""
    
    def _create_sensitivity_patterns(self, reg_field: RegulatoryField) -> List[SensitivityPattern]:
        """Create sensitivity patterns from regulatory field"""
        patterns = []
        
        # Create exact match patterns for each alias
        for alias in reg_field.aliases:
            pattern_id = hashlib.md5(f"{alias}_{reg_field.category}".encode()).hexdigest()[:16]
            
            pattern = SensitivityPattern(
                pattern_id=pattern_id,
                pattern_name=f"{reg_field.category}_{alias}",
                pattern_type="exact",
                pattern_value=alias,
                pii_type=reg_field.pii_type,
                risk_level=reg_field.risk_level,
                applicable_regulations=reg_field.regulations,
                confidence=reg_field.confidence,
                aliases=reg_field.aliases,
                created_date=datetime.now()
            )
            
            patterns.append(pattern)
            
            # Cache the pattern
            self.pattern_cache[pattern_id] = pattern
        
        # Create regex patterns for common variations
        base_name = reg_field.field_name.lower()
        regex_variations = [
            f".*{base_name}.*",
            f"{base_name}_.*",
            f".*_{base_name}",
            f"{base_name}[0-9]*",
            f".*{base_name}[0-9]*.*"
        ]
        
        for regex_pattern in regex_variations:
            pattern_id = hashlib.md5(f"{regex_pattern}_{reg_field.category}_regex".encode()).hexdigest()[:16]
            
            pattern = SensitivityPattern(
                pattern_id=pattern_id,
                pattern_name=f"{reg_field.category}_regex_{base_name}",
                pattern_type="regex",
                pattern_value=regex_pattern,
                pii_type=reg_field.pii_type,
                risk_level=reg_field.risk_level,
                applicable_regulations=reg_field.regulations,
                confidence=reg_field.confidence * 0.85,  # Lower confidence for regex
                aliases=reg_field.aliases,
                created_date=datetime.now()
            )
            
            patterns.append(pattern)
            self.pattern_cache[pattern_id] = pattern
        
        return patterns
    
    def get_comprehensive_pattern_database(self) -> Dict[str, Any]:
        """Get comprehensive pattern database from all loaded regulatory data"""
        # Load all regulatory patterns
        hipaa_patterns = self.load_hipaa_patterns()
        gdpr_patterns = self.load_gdpr_patterns()
        alias_mappings = self.load_alias_patterns()
        
        # Combine all patterns
        all_patterns = {}
        all_patterns.update(hipaa_patterns)
        all_patterns.update(gdpr_patterns)
        
        # Create comprehensive database
        pattern_db = {
            'regulatory_fields': self.regulatory_fields,
            'sensitivity_patterns': all_patterns,
            'alias_mappings': self.alias_mappings,
            'pattern_cache': self.pattern_cache,
            'statistics': {
                'total_regulatory_fields': len(self.regulatory_fields),
                'total_patterns': sum(len(patterns) for patterns in all_patterns.values()),
                'total_aliases': len(self.alias_mappings),
                'hipaa_fields': len([f for f in self.regulatory_fields.values() if Regulation.HIPAA in f.regulations]),
                'gdpr_fields': len([f for f in self.regulatory_fields.values() if Regulation.GDPR in f.regulations])
            }
        }
        
        main_logger.info("Comprehensive pattern database created", extra={
            'component': 'regulatory_loader',
            'total_fields': pattern_db['statistics']['total_regulatory_fields'],
            'total_patterns': pattern_db['statistics']['total_patterns'],
            'total_aliases': pattern_db['statistics']['total_aliases']
        })
        
        return pattern_db
    
    def export_pattern_database(self, file_path: str) -> bool:
        """Export pattern database to JSON file"""
        try:
            pattern_db = self.get_comprehensive_pattern_database()
            
            # Convert to JSON-serializable format
            exportable_db = {
                'regulatory_fields': {k: self._regulatory_field_to_dict(v) for k, v in pattern_db['regulatory_fields'].items()},
                'alias_mappings': pattern_db['alias_mappings'],
                'statistics': pattern_db['statistics'],
                'export_timestamp': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(exportable_db, f, indent=2, ensure_ascii=False)
            
            main_logger.info(f"Pattern database exported to {file_path}", extra={
                'component': 'regulatory_loader',
                'file': file_path,
                'total_fields': len(exportable_db['regulatory_fields'])
            })
            
            return True
            
        except Exception as e:
            main_logger.error(f"Error exporting pattern database: {e}", extra={
                'component': 'regulatory_loader',
                'error': str(e)
            })
            return False
    
    def _regulatory_field_to_dict(self, reg_field: RegulatoryField) -> Dict[str, Any]:
        """Convert RegulatoryField to dictionary"""
        return {
            'field_name': reg_field.field_name,
            'aliases': reg_field.aliases,
            'pii_type': reg_field.pii_type.value,
            'risk_level': reg_field.risk_level.value,
            'regulations': [reg.value for reg in reg_field.regulations],
            'category': reg_field.category,
            'confidence': reg_field.confidence,
            'description': reg_field.description,
            'examples': reg_field.examples or [],
            'sub_fields': reg_field.sub_fields or []
        }


# Global instance
regulatory_loader = RegulatoryPatternLoader()