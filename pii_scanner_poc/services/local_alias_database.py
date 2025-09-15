"""
Local Alias and Sensitive Field Database Implementation
Advanced database system for managing field aliases, patterns, and learning from operations
"""

import sqlite3
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import contextmanager
import threading
from fuzzywuzzy import fuzz

from pii_scanner_poc.models.data_models import Regulation, PIIType, RiskLevel
from pii_scanner_poc.models.enhanced_data_models import SensitivityPattern, CompanyAlias, DetectionMethod


@dataclass
class FieldAlias:
    """Represents a field alias mapping"""
    alias_id: str
    standard_field_name: str
    alias_name: str
    confidence_score: float
    pii_type: PIIType
    risk_level: RiskLevel
    applicable_regulations: List[Regulation]
    company_id: Optional[str] = None
    region: Optional[str] = None
    created_date: datetime = None
    last_used: Optional[datetime] = None
    usage_count: int = 0
    validation_status: str = "pending"  # pending, approved, rejected
    created_by: str = "system"
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()


@dataclass
class LearningRecord:
    """Represents a learning record from user feedback or validation"""
    record_id: str
    field_name: str
    table_name: str
    schema_name: str
    detected_pii_type: PIIType
    actual_pii_type: PIIType
    confidence_score: float
    detection_method: DetectionMethod
    user_feedback: str
    is_correct: bool
    created_date: datetime = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()


class LocalAliasDatabase:
    """Advanced local database for alias and pattern management"""
    
    def __init__(self, db_path: str = "data/alias_database.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._lock = threading.RLock()
        
        # Initialize database
        self._initialize_database()
        
        print(f"📚 Local alias database initialized: {self.db_path}")
    
    def _initialize_database(self):
        """Initialize the database schema"""
        
        with self._get_connection() as conn:
            # Field aliases table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS field_aliases (
                    alias_id TEXT PRIMARY KEY,
                    standard_field_name TEXT NOT NULL,
                    alias_name TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    pii_type TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    applicable_regulations TEXT NOT NULL,
                    company_id TEXT,
                    region TEXT,
                    created_date TEXT NOT NULL,
                    last_used TEXT,
                    usage_count INTEGER DEFAULT 0,
                    validation_status TEXT DEFAULT 'pending',
                    created_by TEXT DEFAULT 'system',
                    UNIQUE(alias_name, company_id, region)
                )
            """)
            
            # Learning records table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_records (
                    record_id TEXT PRIMARY KEY,
                    field_name TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    schema_name TEXT NOT NULL,
                    detected_pii_type TEXT NOT NULL,
                    actual_pii_type TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    detection_method TEXT NOT NULL,
                    user_feedback TEXT,
                    is_correct BOOLEAN NOT NULL,
                    created_date TEXT NOT NULL,
                    session_id TEXT
                )
            """)
            
            # Create indexes for learning_records
            conn.execute("CREATE INDEX IF NOT EXISTS idx_field_name ON learning_records (field_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_is_correct ON learning_records (is_correct)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_date ON learning_records (created_date)")
            
            # Pattern performance tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pattern_performance (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_name TEXT NOT NULL,
                    total_matches INTEGER DEFAULT 0,
                    correct_matches INTEGER DEFAULT 0,
                    false_positives INTEGER DEFAULT 0,
                    false_negatives INTEGER DEFAULT 0,
                    accuracy_rate REAL DEFAULT 0.0,
                    last_updated TEXT NOT NULL,
                    performance_data TEXT
                )
            """)
            
            # Company-specific patterns
            conn.execute("""
                CREATE TABLE IF NOT EXISTS company_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    company_id TEXT NOT NULL,
                    pattern_name TEXT NOT NULL,
                    pattern_value TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pii_type TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    created_date TEXT NOT NULL,
                    approved_by TEXT,
                    approval_date TEXT,
                    usage_count INTEGER DEFAULT 0
                )
            """)
            
            # Fuzzy matching cache
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fuzzy_match_cache (
                    cache_id TEXT PRIMARY KEY,
                    source_field TEXT NOT NULL,
                    target_field TEXT NOT NULL,
                    similarity_score REAL NOT NULL,
                    match_type TEXT NOT NULL,
                    created_date TEXT NOT NULL
                )
            """)
            
            # Create indexes for fuzzy_match_cache
            conn.execute("CREATE INDEX IF NOT EXISTS idx_source_field ON fuzzy_match_cache (source_field)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_similarity ON fuzzy_match_cache (similarity_score)")
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with automatic cleanup"""
        with self._lock:
            conn = sqlite3.connect(str(self.db_path), timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
    
    def add_field_alias(self, alias: FieldAlias) -> bool:
        """Add a new field alias to the database"""
        
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO field_aliases 
                    (alias_id, standard_field_name, alias_name, confidence_score,
                     pii_type, risk_level, applicable_regulations, company_id, region,
                     created_date, last_used, usage_count, validation_status, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alias.alias_id,
                    alias.standard_field_name,
                    alias.alias_name,
                    alias.confidence_score,
                    alias.pii_type.value,
                    alias.risk_level.value,
                    json.dumps([reg.value for reg in alias.applicable_regulations]),
                    alias.company_id,
                    alias.region,
                    alias.created_date.isoformat(),
                    alias.last_used.isoformat() if alias.last_used else None,
                    alias.usage_count,
                    alias.validation_status,
                    alias.created_by
                ))
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"❌ Error adding field alias: {e}")
            return False
    
    def find_alias_matches(self, field_name: str, company_id: str = None, 
                          region: str = None, similarity_threshold: float = 0.8) -> List[FieldAlias]:
        """Find matching aliases for a field name"""
        
        matches = []
        
        with self._get_connection() as conn:
            # Exact match first
            cursor = conn.execute("""
                SELECT * FROM field_aliases 
                WHERE alias_name = ? 
                AND (company_id = ? OR company_id IS NULL)
                AND (region = ? OR region IS NULL)
                AND validation_status = 'approved'
                ORDER BY confidence_score DESC
            """, (field_name.lower(), company_id, region))
            
            for row in cursor.fetchall():
                alias = self._row_to_field_alias(dict(row))
                matches.append(alias)
            
            # If no exact matches, try fuzzy matching
            if not matches:
                cursor = conn.execute("""
                    SELECT * FROM field_aliases 
                    WHERE (company_id = ? OR company_id IS NULL)
                    AND (region = ? OR region IS NULL)
                    AND validation_status = 'approved'
                """, (company_id, region))
                
                for row in cursor.fetchall():
                    alias_data = dict(row)
                    similarity = fuzz.ratio(field_name.lower(), alias_data['alias_name'].lower()) / 100.0
                    
                    if similarity >= similarity_threshold:
                        alias = self._row_to_field_alias(alias_data)
                        alias.confidence_score *= similarity  # Adjust confidence based on similarity
                        matches.append(alias)
        
        # Sort by confidence score
        matches.sort(key=lambda x: x.confidence_score, reverse=True)
        return matches
    
    def _row_to_field_alias(self, row_data: Dict) -> FieldAlias:
        """Convert database row to FieldAlias object"""
        
        return FieldAlias(
            alias_id=row_data['alias_id'],
            standard_field_name=row_data['standard_field_name'],
            alias_name=row_data['alias_name'],
            confidence_score=row_data['confidence_score'],
            pii_type=PIIType(row_data['pii_type']),
            risk_level=RiskLevel(row_data['risk_level']),
            applicable_regulations=[Regulation(reg) for reg in json.loads(row_data['applicable_regulations'])],
            company_id=row_data['company_id'],
            region=row_data['region'],
            created_date=datetime.fromisoformat(row_data['created_date']),
            last_used=datetime.fromisoformat(row_data['last_used']) if row_data['last_used'] else None,
            usage_count=row_data['usage_count'],
            validation_status=row_data['validation_status'],
            created_by=row_data['created_by']
        )
    
    def record_learning_feedback(self, learning_record: LearningRecord) -> bool:
        """Record learning feedback from user validation"""
        
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO learning_records 
                    (record_id, field_name, table_name, schema_name,
                     detected_pii_type, actual_pii_type, confidence_score,
                     detection_method, user_feedback, is_correct,
                     created_date, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    learning_record.record_id,
                    learning_record.field_name,
                    learning_record.table_name,
                    learning_record.schema_name,
                    learning_record.detected_pii_type.value,
                    learning_record.actual_pii_type.value,
                    learning_record.confidence_score,
                    learning_record.detection_method.value,
                    learning_record.user_feedback,
                    learning_record.is_correct,
                    learning_record.created_date.isoformat(),
                    learning_record.session_id
                ))
                conn.commit()
                
                # If feedback indicates incorrect detection, create alias for improvement
                if not learning_record.is_correct and learning_record.actual_pii_type != PIIType.NONE:
                    self._create_alias_from_feedback(learning_record)
                
                return True
                
        except sqlite3.Error as e:
            print(f"❌ Error recording learning feedback: {e}")
            return False
    
    def _create_alias_from_feedback(self, learning_record: LearningRecord):
        """Create new alias based on user feedback"""
        
        # Generate alias ID
        alias_id = hashlib.md5(
            f"{learning_record.field_name}_{learning_record.actual_pii_type.value}".encode()
        ).hexdigest()[:16]
        
        # Create alias
        alias = FieldAlias(
            alias_id=alias_id,
            standard_field_name=learning_record.actual_pii_type.value.lower(),
            alias_name=learning_record.field_name.lower(),
            confidence_score=0.85,  # Start with high confidence from user feedback
            pii_type=learning_record.actual_pii_type,
            risk_level=self._infer_risk_level(learning_record.actual_pii_type),
            applicable_regulations=[Regulation.GDPR],  # Default, can be updated
            validation_status="approved",  # User feedback is considered approved
            created_by="user_feedback"
        )
        
        self.add_field_alias(alias)
    
    def _infer_risk_level(self, pii_type: PIIType) -> RiskLevel:
        """Infer risk level based on PII type"""
        
        high_risk_types = {PIIType.EMAIL, PIIType.NAME, PIIType.PHONE, PIIType.SSN, PIIType.MEDICAL, PIIType.FINANCIAL}
        medium_risk_types = {PIIType.ADDRESS, PIIType.ID, PIIType.OTHER}
        
        if pii_type in high_risk_types:
            return RiskLevel.HIGH
        elif pii_type in medium_risk_types:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def update_pattern_performance(self, pattern_id: str, is_correct_match: bool, 
                                 additional_data: Dict = None):
        """Update pattern performance metrics"""
        
        with self._get_connection() as conn:
            # Get current performance data
            cursor = conn.execute("""
                SELECT * FROM pattern_performance WHERE pattern_id = ?
            """, (pattern_id,))
            
            row = cursor.fetchone()
            
            if row:
                # Update existing record
                total_matches = row['total_matches'] + 1
                correct_matches = row['correct_matches'] + (1 if is_correct_match else 0)
                false_positives = row['false_positives'] + (0 if is_correct_match else 1)
                accuracy_rate = correct_matches / total_matches if total_matches > 0 else 0.0
                
                conn.execute("""
                    UPDATE pattern_performance 
                    SET total_matches = ?, correct_matches = ?, false_positives = ?,
                        accuracy_rate = ?, last_updated = ?, performance_data = ?
                    WHERE pattern_id = ?
                """, (
                    total_matches, correct_matches, false_positives,
                    accuracy_rate, datetime.now().isoformat(),
                    json.dumps(additional_data or {}), pattern_id
                ))
            else:
                # Create new record
                conn.execute("""
                    INSERT INTO pattern_performance 
                    (pattern_id, pattern_name, total_matches, correct_matches,
                     false_positives, accuracy_rate, last_updated, performance_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern_id, pattern_id, 1, 1 if is_correct_match else 0,
                    0 if is_correct_match else 1, 1.0 if is_correct_match else 0.0,
                    datetime.now().isoformat(), json.dumps(additional_data or {})
                ))
            
            conn.commit()
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        
        with self._get_connection() as conn:
            stats = {}
            
            # Alias statistics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_aliases,
                    COUNT(CASE WHEN validation_status = 'approved' THEN 1 END) as approved_aliases,
                    COUNT(CASE WHEN validation_status = 'pending' THEN 1 END) as pending_aliases,
                    AVG(confidence_score) as avg_confidence,
                    SUM(usage_count) as total_usage
                FROM field_aliases
            """)
            
            alias_stats = dict(cursor.fetchone())
            stats['aliases'] = alias_stats
            
            # Learning statistics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_feedback,
                    COUNT(CASE WHEN is_correct = 1 THEN 1 END) as correct_predictions,
                    COUNT(CASE WHEN is_correct = 0 THEN 1 END) as incorrect_predictions,
                    AVG(confidence_score) as avg_confidence_score
                FROM learning_records
                WHERE created_date >= ?
            """, ((datetime.now() - timedelta(days=30)).isoformat(),))
            
            learning_stats = dict(cursor.fetchone())
            if learning_stats['total_feedback'] > 0:
                learning_stats['accuracy_rate'] = learning_stats['correct_predictions'] / learning_stats['total_feedback']
            else:
                learning_stats['accuracy_rate'] = 0.0
            
            stats['learning'] = learning_stats
            
            # Pattern performance
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_patterns,
                    AVG(accuracy_rate) as avg_accuracy,
                    SUM(total_matches) as total_pattern_matches
                FROM pattern_performance
            """)
            
            pattern_stats = dict(cursor.fetchone())
            stats['patterns'] = pattern_stats
            
            # Top performing aliases
            cursor = conn.execute("""
                SELECT alias_name, usage_count, confidence_score, pii_type
                FROM field_aliases 
                ORDER BY usage_count DESC 
                LIMIT 10
            """)
            
            stats['top_aliases'] = [dict(row) for row in cursor.fetchall()]
            
        return stats
    
    def bulk_import_aliases(self, aliases_data: List[Dict[str, Any]], 
                           company_id: str = None, created_by: str = "bulk_import") -> Dict[str, int]:
        """Bulk import aliases from external data"""
        
        results = {'imported': 0, 'skipped': 0, 'errors': 0}
        
        for alias_data in aliases_data:
            try:
                # Generate alias ID
                alias_id = hashlib.md5(
                    f"{alias_data['alias_name']}_{alias_data.get('pii_type', 'unknown')}".encode()
                ).hexdigest()[:16]
                
                alias = FieldAlias(
                    alias_id=alias_id,
                    standard_field_name=alias_data.get('standard_field_name', ''),
                    alias_name=alias_data['alias_name'].lower(),
                    confidence_score=float(alias_data.get('confidence_score', 0.8)),
                    pii_type=PIIType(alias_data.get('pii_type', PIIType.OTHER.value)),
                    risk_level=RiskLevel(alias_data.get('risk_level', RiskLevel.MEDIUM.value)),
                    applicable_regulations=[Regulation.GDPR if reg == 'GDPR' else Regulation.HIPAA 
                                          for reg in alias_data.get('regulations', ['GDPR'])],
                    company_id=company_id,
                    created_by=created_by,
                    validation_status="pending"  # Require approval for bulk imports
                )
                
                if self.add_field_alias(alias):
                    results['imported'] += 1
                else:
                    results['skipped'] += 1
                    
            except Exception as e:
                print(f"❌ Error importing alias {alias_data.get('alias_name', 'unknown')}: {e}")
                results['errors'] += 1
        
        return results
    
    def export_aliases(self, company_id: str = None, validation_status: str = "approved") -> List[Dict[str, Any]]:
        """Export aliases for backup or sharing"""
        
        with self._get_connection() as conn:
            query = """
                SELECT * FROM field_aliases 
                WHERE validation_status = ?
            """
            params = [validation_status]
            
            if company_id:
                query += " AND (company_id = ? OR company_id IS NULL)"
                params.append(company_id)
            
            cursor = conn.execute(query, params)
            
            aliases = []
            for row in cursor.fetchall():
                alias_data = dict(row)
                # Convert datetime strings back to readable format
                alias_data['created_date'] = alias_data['created_date']
                alias_data['applicable_regulations'] = json.loads(alias_data['applicable_regulations'])
                aliases.append(alias_data)
            
            return aliases
    
    def approve_pending_aliases(self, approver: str, alias_ids: List[str] = None) -> int:
        """Approve pending aliases"""
        
        with self._get_connection() as conn:
            if alias_ids:
                placeholders = ','.join(['?' for _ in alias_ids])
                cursor = conn.execute(f"""
                    UPDATE field_aliases 
                    SET validation_status = 'approved', created_by = ?
                    WHERE alias_id IN ({placeholders}) AND validation_status = 'pending'
                """, [approver] + alias_ids)
            else:
                cursor = conn.execute("""
                    UPDATE field_aliases 
                    SET validation_status = 'approved', created_by = ?
                    WHERE validation_status = 'pending'
                """, (approver,))
            
            conn.commit()
            return cursor.rowcount
    
    def cleanup_old_records(self, days_old: int = 365) -> Dict[str, int]:
        """Clean up old records to maintain database performance"""
        
        cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
        results = {'learning_records': 0, 'fuzzy_cache': 0}
        
        with self._get_connection() as conn:
            # Clean old learning records (keep recent ones for analysis)
            cursor = conn.execute("""
                DELETE FROM learning_records 
                WHERE created_date < ? AND is_correct = 1
            """, (cutoff_date,))
            results['learning_records'] = cursor.rowcount
            
            # Clean old fuzzy match cache
            cursor = conn.execute("""
                DELETE FROM fuzzy_match_cache 
                WHERE created_date < ?
            """, (cutoff_date,))
            results['fuzzy_cache'] = cursor.rowcount
            
            conn.commit()
        
        return results


# Integration class for the main PII scanner
class AliasIntegratedClassifier:
    """Enhanced classifier that integrates with the alias database"""
    
    def __init__(self, alias_db: LocalAliasDatabase):
        self.alias_db = alias_db
        self.session_feedback = []  # Store feedback for batch processing
    
    def enhanced_field_classification(self, field_name: str, table_context: List[str],
                                    company_id: str = None, region: str = None) -> Optional[Dict[str, Any]]:
        """Enhanced field classification using alias database"""
        
        # Check alias database first
        alias_matches = self.alias_db.find_alias_matches(
            field_name, company_id, region, similarity_threshold=0.8
        )
        
        if alias_matches:
            best_match = alias_matches[0]
            
            # Update usage statistics
            self.alias_db.update_pattern_performance(
                best_match.alias_id, True  # Assume correct for now
            )
            
            return {
                'field_name': field_name,
                'pii_type': best_match.pii_type,
                'risk_level': best_match.risk_level,
                'confidence_score': best_match.confidence_score,
                'detection_method': 'alias_database',
                'source_alias': best_match.alias_name,
                'applicable_regulations': best_match.applicable_regulations
            }
        
        return None  # Fall back to standard classification
    
    def record_classification_feedback(self, field_name: str, table_name: str,
                                     detected_type: PIIType, actual_type: PIIType,
                                     is_correct: bool, confidence: float,
                                     user_feedback: str = ""):
        """Record user feedback for continuous learning"""
        
        record = LearningRecord(
            record_id=hashlib.md5(f"{field_name}_{table_name}_{datetime.now().isoformat()}".encode()).hexdigest()[:16],
            field_name=field_name,
            table_name=table_name,
            schema_name="unknown",  # Could be enhanced with actual schema name
            detected_pii_type=detected_type,
            actual_pii_type=actual_type,
            confidence_score=confidence,
            detection_method=DetectionMethod.LOCAL_PATTERN,
            user_feedback=user_feedback,
            is_correct=is_correct
        )
        
        self.alias_db.record_learning_feedback(record)
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get learning and performance statistics"""
        return self.alias_db.get_performance_statistics()


# Global instances
alias_database = LocalAliasDatabase()
alias_classifier = AliasIntegratedClassifier(alias_database)