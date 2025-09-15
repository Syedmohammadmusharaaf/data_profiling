#!/usr/bin/env python3
"""
Alias Database Management CLI
Command-line interface for managing the local alias and pattern database
"""

import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from pii_scanner_poc.services.local_alias_database import alias_database, FieldAlias, LearningRecord
    from pii_scanner_poc.models.data_models import PIIType, RiskLevel, Regulation
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)


class AliasManagementCLI:
    """Command-line interface for alias database management"""
    
    def __init__(self):
        self.db = alias_database
    
    def show_help(self):
        """Display help information"""
        print("""
🏛️ Alias Database Management CLI

COMMANDS:
  add-alias      Add a new field alias
  list-aliases   List all aliases (with optional filters)
  import-csv     Import aliases from CSV file
  export-csv     Export aliases to CSV file
  approve        Approve pending aliases
  stats          Show database statistics
  search         Search for aliases by field name
  performance    Show pattern performance metrics
  cleanup        Clean up old records
  feedback       Add learning feedback record
  help           Show this help message

EXAMPLES:
  python alias_management.py add-alias --field-name "cust_email" --pii-type "EMAIL" --confidence 0.95
  python alias_management.py list-aliases --status approved --company mycompany
  python alias_management.py import-csv --file aliases.csv --company mycompany
  python alias_management.py stats
  python alias_management.py search --field "email"

For detailed help on a specific command, use:
  python alias_management.py <command> --help
        """)
    
    def add_alias(self, args):
        """Add a new field alias"""
        if not args.field_name or not args.pii_type:
            print("❌ --field-name and --pii-type are required")
            return
        
        try:
            # Generate alias ID
            import hashlib
            alias_id = hashlib.md5(f"{args.field_name}_{args.pii_type}".encode()).hexdigest()[:16]
            
            alias = FieldAlias(
                alias_id=alias_id,
                standard_field_name=args.pii_type.lower(),
                alias_name=args.field_name.lower(),
                confidence_score=float(args.confidence or 0.8),
                pii_type=PIIType(args.pii_type),
                risk_level=RiskLevel(args.risk_level or "MEDIUM"),
                applicable_regulations=[Regulation(reg) for reg in (args.regulations or ["GDPR"]).split(",")],
                company_id=args.company,
                region=args.region,
                validation_status=args.status or "pending",
                created_by=args.created_by or "cli"
            )
            
            if self.db.add_field_alias(alias):
                print(f"✅ Added alias: {args.field_name} -> {args.pii_type}")
            else:
                print("❌ Failed to add alias")
                
        except Exception as e:
            print(f"❌ Error adding alias: {e}")
    
    def list_aliases(self, args):
        """List aliases with optional filters"""
        print("\n📋 Field Aliases")
        print("-" * 80)
        
        try:
            aliases = self.db.export_aliases(
                company_id=args.company,
                validation_status=args.status or "approved"
            )
            
            if not aliases:
                print("No aliases found matching criteria")
                return
            
            # Display aliases in table format
            print(f"{'Alias Name':<25} {'PII Type':<12} {'Risk':<8} {'Confidence':<10} {'Status':<10} {'Company':<12}")
            print("-" * 80)
            
            for alias in aliases[:50]:  # Limit to 50 for readability
                print(f"{alias['alias_name']:<25} "
                      f"{alias['pii_type']:<12} "
                      f"{alias['risk_level']:<8} "
                      f"{alias['confidence_score']:<10.2f} "
                      f"{alias['validation_status']:<10} "
                      f"{alias['company_id'] or 'global':<12}")
            
            if len(aliases) > 50:
                print(f"\n... and {len(aliases) - 50} more aliases")
            
            print(f"\nTotal: {len(aliases)} aliases")
            
        except Exception as e:
            print(f"❌ Error listing aliases: {e}")
    
    def import_csv(self, args):
        """Import aliases from CSV file"""
        if not args.file:
            print("❌ --file is required")
            return
        
        csv_file = Path(args.file)
        if not csv_file.exists():
            print(f"❌ File not found: {csv_file}")
            return
        
        try:
            aliases_data = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    aliases_data.append({
                        'alias_name': row.get('alias_name', ''),
                        'standard_field_name': row.get('standard_field_name', ''),
                        'pii_type': row.get('pii_type', 'OTHER'),
                        'risk_level': row.get('risk_level', 'MEDIUM'),
                        'confidence_score': row.get('confidence_score', '0.8'),
                        'regulations': row.get('regulations', 'GDPR').split(',')
                    })
            
            results = self.db.bulk_import_aliases(
                aliases_data, 
                company_id=args.company,
                created_by=args.created_by or "csv_import"
            )
            
            print(f"✅ Import completed:")
            print(f"   Imported: {results['imported']}")
            print(f"   Skipped: {results['skipped']}")
            print(f"   Errors: {results['errors']}")
            
        except Exception as e:
            print(f"❌ Error importing CSV: {e}")
    
    def export_csv(self, args):
        """Export aliases to CSV file"""
        output_file = Path(args.output or f"aliases_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        
        try:
            aliases = self.db.export_aliases(
                company_id=args.company,
                validation_status=args.status or "approved"
            )
            
            if not aliases:
                print("No aliases to export")
                return
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = [
                    'alias_name', 'standard_field_name', 'pii_type', 'risk_level',
                    'confidence_score', 'applicable_regulations', 'company_id',
                    'region', 'validation_status', 'created_date', 'usage_count'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for alias in aliases:
                    # Flatten the data for CSV
                    row = {
                        'alias_name': alias['alias_name'],
                        'standard_field_name': alias['standard_field_name'],
                        'pii_type': alias['pii_type'],
                        'risk_level': alias['risk_level'],
                        'confidence_score': alias['confidence_score'],
                        'applicable_regulations': ','.join(alias['applicable_regulations']),
                        'company_id': alias['company_id'] or '',
                        'region': alias['region'] or '',
                        'validation_status': alias['validation_status'],
                        'created_date': alias['created_date'],
                        'usage_count': alias['usage_count']
                    }
                    writer.writerow(row)
            
            print(f"✅ Exported {len(aliases)} aliases to: {output_file}")
            
        except Exception as e:
            print(f"❌ Error exporting CSV: {e}")
    
    def approve_aliases(self, args):
        """Approve pending aliases"""
        try:
            count = self.db.approve_pending_aliases(
                approver=args.approver or "admin",
                alias_ids=args.alias_ids.split(',') if args.alias_ids else None
            )
            
            print(f"✅ Approved {count} aliases")
            
        except Exception as e:
            print(f"❌ Error approving aliases: {e}")
    
    def show_stats(self, args):
        """Show database statistics"""
        try:
            stats = self.db.get_performance_statistics()

            print("\n📊 Alias Database Statistics")
            print("=" * 50)

            # Alias statistics
            alias_stats = stats['aliases']
            print(f"📚 Aliases:")
            print(f"   Total: {alias_stats.get('total_aliases', 0)}")
            print(f"   Approved: {alias_stats.get('approved_aliases', 0)}")
            print(f"   Pending: {alias_stats.get('pending_aliases', 0)}")
            avg_conf = alias_stats.get('avg_confidence')
            print(f"   Average Confidence: {avg_conf:.2f}" if avg_conf is not None else "   Average Confidence: 0.00")
            print(f"   Total Usage: {alias_stats.get('total_usage', 0)}")

            # Learning statistics
            learning_stats = stats['learning']
            print(f"\n🧠 Learning (Last 30 Days):")
            print(f"   Total Feedback: {learning_stats.get('total_feedback', 0)}")
            print(f"   Correct Predictions: {learning_stats.get('correct_predictions', 0)}")
            print(f"   Incorrect Predictions: {learning_stats.get('incorrect_predictions', 0)}")
            acc_rate = learning_stats.get('accuracy_rate')
            print(f"   Accuracy Rate: {acc_rate:.2%}" if acc_rate is not None else "   Accuracy Rate: 0.00%")

            # Pattern performance
            pattern_stats = stats['patterns']
            print(f"\n📈 Pattern Performance:")
            print(f"   Total Patterns: {pattern_stats.get('total_patterns', 0)}")
            avg_acc = pattern_stats.get('avg_accuracy')
            print(f"   Average Accuracy: {avg_acc:.2%}" if avg_acc is not None else "   Average Accuracy: 0.00%")
            print(f"   Total Matches: {pattern_stats.get('total_pattern_matches', 0)}")

            # Top aliases
            if stats.get('top_aliases'):
                print(f"\n🏆 Top Used Aliases:")
                for i, alias in enumerate(stats['top_aliases'][:5], 1):
                    print(f"   {i}. {alias['alias_name']} ({alias['pii_type']}) - Used {alias['usage_count']} times")

        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
    
    def search_aliases(self, args):
        """Search for aliases by field name"""
        if not args.field:
            print("❌ --field is required")
            return
        
        try:
            matches = self.db.find_alias_matches(
                field_name=args.field,
                company_id=args.company,
                region=args.region,
                similarity_threshold=float(args.threshold or 0.8)
            )
            
            if not matches:
                print(f"No matches found for '{args.field}'")
                return
            
            print(f"\n🔍 Search Results for '{args.field}'")
            print("-" * 60)
            
            for i, match in enumerate(matches, 1):
                print(f"{i}. {match.alias_name}")
                print(f"   PII Type: {match.pii_type.value}")
                print(f"   Risk Level: {match.risk_level.value}")
                print(f"   Confidence: {match.confidence_score:.2f}")
                print(f"   Company: {match.company_id or 'global'}")
                print(f"   Status: {match.validation_status}")
                print()
            
        except Exception as e:
            print(f"❌ Error searching aliases: {e}")
    
    def cleanup_database(self, args):
        """Clean up old records"""
        try:
            days_old = int(args.days or 365)
            results = self.db.cleanup_old_records(days_old)
            
            print(f"✅ Cleanup completed:")
            print(f"   Learning records removed: {results['learning_records']}")
            print(f"   Fuzzy cache entries removed: {results['fuzzy_cache']}")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    def add_feedback(self, args):
        """Add learning feedback record"""
        if not all([args.field_name, args.table_name, args.detected_type, args.actual_type]):
            print("❌ --field-name, --table-name, --detected-type, and --actual-type are required")
            return
        
        try:
            import hashlib
            record_id = hashlib.md5(f"{args.field_name}_{args.table_name}_{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            
            record = LearningRecord(
                record_id=record_id,
                field_name=args.field_name,
                table_name=args.table_name,
                schema_name=args.schema_name or "unknown",
                detected_pii_type=PIIType(args.detected_type),
                actual_pii_type=PIIType(args.actual_type),
                confidence_score=float(args.confidence or 0.5),
                detection_method=args.method or "LOCAL_PATTERN",
                user_feedback=args.feedback or "",
                is_correct=args.detected_type == args.actual_type
            )
            
            if self.db.record_learning_feedback(record):
                print(f"✅ Added feedback record for: {args.field_name}")
            else:
                print("❌ Failed to add feedback record")
                
        except Exception as e:
            print(f"❌ Error adding feedback: {e}")


def main():
    """Main CLI execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Alias Database Management CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add alias command
    add_parser = subparsers.add_parser('add-alias', help='Add a new field alias')
    add_parser.add_argument('--field-name', required=True, help='Field name/alias')
    add_parser.add_argument('--pii-type', required=True, help='PII type (EMAIL, NAME, PHONE, etc.)')
    add_parser.add_argument('--risk-level', help='Risk level (HIGH, MEDIUM, LOW)')
    add_parser.add_argument('--confidence', type=float, help='Confidence score (0.0-1.0)')
    add_parser.add_argument('--regulations', help='Comma-separated regulations (GDPR,HIPAA,CCPA)')
    add_parser.add_argument('--company', help='Company ID')
    add_parser.add_argument('--region', help='Region')
    add_parser.add_argument('--status', help='Validation status (pending, approved, rejected)')
    add_parser.add_argument('--created-by', help='Creator name')
    
    # List aliases command
    list_parser = subparsers.add_parser('list-aliases', help='List aliases')
    list_parser.add_argument('--status', help='Filter by validation status')
    list_parser.add_argument('--company', help='Filter by company ID')
    
    # Import CSV command
    import_parser = subparsers.add_parser('import-csv', help='Import aliases from CSV')
    import_parser.add_argument('--file', required=True, help='CSV file path')
    import_parser.add_argument('--company', help='Company ID for imported aliases')
    import_parser.add_argument('--created-by', help='Creator name')
    
    # Export CSV command
    export_parser = subparsers.add_parser('export-csv', help='Export aliases to CSV')
    export_parser.add_argument('--output', help='Output file path')
    export_parser.add_argument('--company', help='Filter by company ID')
    export_parser.add_argument('--status', help='Filter by validation status')
    
    # Approve command
    approve_parser = subparsers.add_parser('approve', help='Approve pending aliases')
    approve_parser.add_argument('--approver', help='Approver name')
    approve_parser.add_argument('--alias-ids', help='Comma-separated alias IDs (leave empty for all)')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search aliases')
    search_parser.add_argument('--field', required=True, help='Field name to search for')
    search_parser.add_argument('--company', help='Company ID filter')
    search_parser.add_argument('--region', help='Region filter')
    search_parser.add_argument('--threshold', help='Similarity threshold (0.0-1.0)')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old records')
    cleanup_parser.add_argument('--days', help='Records older than this many days (default: 365)')
    
    # Feedback command
    feedback_parser = subparsers.add_parser('feedback', help='Add learning feedback')
    feedback_parser.add_argument('--field-name', required=True, help='Field name')
    feedback_parser.add_argument('--table-name', required=True, help='Table name')
    feedback_parser.add_argument('--detected-type', required=True, help='Detected PII type')
    feedback_parser.add_argument('--actual-type', required=True, help='Actual PII type')
    feedback_parser.add_argument('--schema-name', help='Schema name')
    feedback_parser.add_argument('--confidence', type=float, help='Detection confidence')
    feedback_parser.add_argument('--method', help='Detection method')
    feedback_parser.add_argument('--feedback', help='User feedback text')
    
    # Help command
    subparsers.add_parser('help', help='Show help information')
    
    args = parser.parse_args()
    
    if not args.command or args.command == 'help':
        cli = AliasManagementCLI()
        cli.show_help()
        return
    
    try:
        cli = AliasManagementCLI()
        
        if args.command == 'add-alias':
            cli.add_alias(args)
        elif args.command == 'list-aliases':
            cli.list_aliases(args)
        elif args.command == 'import-csv':
            cli.import_csv(args)
        elif args.command == 'export-csv':
            cli.export_csv(args)
        elif args.command == 'approve':
            cli.approve_aliases(args)
        elif args.command == 'stats':
            cli.show_stats(args)
        elif args.command == 'search':
            cli.search_aliases(args)
        elif args.command == 'cleanup':
            cli.cleanup_database(args)
        elif args.command == 'feedback':
            cli.add_feedback(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            cli.show_help()
            
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


def show_stats():
    """Standalone function to show alias database statistics (for main.py import)"""
    try:
        cli = AliasManagementCLI()
        # Create a mock args object with no specific filters
        class MockArgs:
            pass
        args = MockArgs()
        cli.show_stats(args)
        return 0
    except Exception as e:
        print(f"❌ Error showing stats: {e}")
        return 1


if __name__ == "__main__":
    main()