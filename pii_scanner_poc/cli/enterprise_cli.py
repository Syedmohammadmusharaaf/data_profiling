#!/usr/bin/env python3
"""
PII Scanner Enterprise CLI - Enhanced Command Line Interface
Provides comprehensive CLI functionality for enterprise-grade PII scanning
"""

import os
import sys
import argparse
import asyncio
import time
from typing import List, Dict, Optional
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pii_scanner_poc.core.pii_scanner_facade import PIIScannerFacade
from pii_scanner_poc.core.hybrid_classification_orchestrator import HybridClassificationOrchestrator
from pii_scanner_poc.services.database_service import database_service
from pii_scanner_poc.models.data_models import Regulation
from pii_scanner_poc.utils.logging_config import main_logger
from pii_scanner_poc.utils.performance_optimizer import PerformanceOptimizer


class EnterpriseCLI:
    """Enhanced CLI for enterprise PII scanning with performance optimizations"""
    
    def __init__(self):
        self.scanner = PIIScannerFacade()
        self.orchestrator = HybridClassificationOrchestrator()
        self.optimizer = PerformanceOptimizer()
        self.results_cache = {}
        
    def create_parser(self) -> argparse.ArgumentParser:
        """Create comprehensive argument parser"""
        parser = argparse.ArgumentParser(
            description="PII Scanner Enterprise - High-performance data privacy compliance tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Fast scan with performance optimization
  python enterprise_cli.py scan --file schema.ddl --regulations GDPR HIPAA --fast
  
  # Batch processing multiple files
  python enterprise_cli.py batch --input-dir /path/to/schemas --output-dir /path/to/reports
  
  # Parallel processing for large datasets
  python enterprise_cli.py scan --file large_schema.ddl --parallel --workers 8
  
  # Performance benchmarking
  python enterprise_cli.py benchmark --file test_schema.ddl --iterations 10
  
  # Cache management
  python enterprise_cli.py cache --clear --stats
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Scan command
        scan_parser = subparsers.add_parser('scan', help='Scan schema files for PII/PHI')
        self._add_scan_arguments(scan_parser)
        
        # Batch command
        batch_parser = subparsers.add_parser('batch', help='Batch process multiple files')
        self._add_batch_arguments(batch_parser)
        
        # Benchmark command
        benchmark_parser = subparsers.add_parser('benchmark', help='Performance benchmarking')
        self._add_benchmark_arguments(benchmark_parser)
        
        # Cache command
        cache_parser = subparsers.add_parser('cache', help='Cache management')
        self._add_cache_arguments(cache_parser)
        
        # Server command
        server_parser = subparsers.add_parser('server', help='Start web server')
        self._add_server_arguments(server_parser)
        
        return parser
    
    def _add_scan_arguments(self, parser: argparse.ArgumentParser):
        """Add scan command arguments"""
        parser.add_argument('--file', '-f', required=True, help='Schema file to scan')
        parser.add_argument('--regulations', '-r', nargs='+', 
                          choices=['GDPR', 'HIPAA', 'CCPA'], 
                          default=['GDPR'], help='Regulations to check against')
        parser.add_argument('--output', '-o', help='Output file path')
        parser.add_argument('--format', choices=['json', 'csv', 'html'], 
                          default='json', help='Output format')
        parser.add_argument('--tables', nargs='+', help='Specific tables to scan')
        parser.add_argument('--fast', action='store_true', 
                          help='Enable fast mode with performance optimizations')
        parser.add_argument('--parallel', action='store_true', 
                          help='Enable parallel processing')
        parser.add_argument('--workers', type=int, default=mp.cpu_count(), 
                          help='Number of worker processes for parallel execution')
        parser.add_argument('--cache', action='store_true', 
                          help='Enable intelligent caching')
        parser.add_argument('--streaming', action='store_true', 
                          help='Enable streaming processing for large files')
        parser.add_argument('--verbose', '-v', action='store_true', 
                          help='Verbose output')
    
    def _add_batch_arguments(self, parser: argparse.ArgumentParser):
        """Add batch command arguments"""
        parser.add_argument('--input-dir', required=True, help='Input directory with schema files')
        parser.add_argument('--output-dir', required=True, help='Output directory for reports')
        parser.add_argument('--pattern', default='*.ddl', help='File pattern to match')
        parser.add_argument('--regulations', nargs='+', 
                          choices=['GDPR', 'HIPAA', 'CCPA'], 
                          default=['GDPR'], help='Regulations to check against')
        parser.add_argument('--workers', type=int, default=mp.cpu_count(), 
                          help='Number of parallel workers')
        parser.add_argument('--resume', action='store_true', 
                          help='Resume interrupted batch processing')
    
    def _add_benchmark_arguments(self, parser: argparse.ArgumentParser):
        """Add benchmark command arguments"""
        parser.add_argument('--file', required=True, help='Schema file for benchmarking')
        parser.add_argument('--iterations', type=int, default=5, help='Number of iterations')
        parser.add_argument('--warmup', type=int, default=2, help='Warmup iterations')
        parser.add_argument('--profile', action='store_true', help='Enable detailed profiling')
    
    def _add_cache_arguments(self, parser: argparse.ArgumentParser):
        """Add cache command arguments"""
        parser.add_argument('--clear', action='store_true', help='Clear cache')
        parser.add_argument('--stats', action='store_true', help='Show cache statistics')
        parser.add_argument('--optimize', action='store_true', help='Optimize cache')
    
    def _add_server_arguments(self, parser: argparse.ArgumentParser):
        """Add server command arguments"""
        parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
        parser.add_argument('--port', type=int, default=8001, help='Port to bind to')
        parser.add_argument('--workers', type=int, default=1, help='Number of server workers')
    
    async def handle_scan(self, args) -> Dict:
        """Handle scan command with performance optimizations"""
        start_time = time.time()
        
        if args.verbose:
            print(f"🔍 Starting PII scan of {args.file}")
            print(f"📋 Regulations: {', '.join(args.regulations)}")
            print(f"⚡ Fast mode: {'Enabled' if args.fast else 'Disabled'}")
            print(f"🔄 Parallel processing: {'Enabled' if args.parallel else 'Disabled'}")
        
        # Performance optimizations
        if args.fast:
            self.optimizer.enable_fast_mode()
        
        if args.cache:
            self.optimizer.enable_intelligent_caching()
        
        if args.streaming:
            self.optimizer.enable_streaming_mode()
        
        try:
            # Configure parallel processing
            if args.parallel:
                results = await self._parallel_scan(args)
            else:
                results = await self._sequential_scan(args)
            
            # Process results
            elapsed_time = time.time() - start_time
            results['performance'] = {
                'elapsed_time': elapsed_time,
                'fast_mode': args.fast,
                'parallel_processing': args.parallel,
                'workers': args.workers if args.parallel else 1
            }
            
            # Output results
            await self._output_results(results, args)
            
            if args.verbose:
                print(f"✅ Scan completed in {elapsed_time:.2f} seconds")
                print(f"📊 Found {len(results.get('findings', []))} potential PII/PHI fields")
            
            return results
            
        except Exception as e:
            main_logger.error(f"Scan failed: {e}")
            if args.verbose:
                print(f"❌ Scan failed: {e}")
            raise
    
    async def _sequential_scan(self, args) -> Dict:
        """Perform sequential scan"""
        result = self.scanner.analyze_schema_file(
            schema_file_path=args.file,
            regulations=args.regulations,
            selected_tables=args.tables,
            output_format=args.format,
            enable_caching=args.cache
        )
        return result
    
    async def _parallel_scan(self, args) -> Dict:
        """Perform parallel scan using multiple workers"""
        if args.verbose:
            print(f"🔄 Using {args.workers} parallel workers")
        
        # Load and split schema data
        schema_data = database_service.load_schema_from_file(args.file)
        chunks = self.optimizer.create_parallel_chunks(schema_data, args.workers)
        
        # Process chunks in parallel
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for i, chunk in enumerate(chunks):
                future = executor.submit(self._process_chunk, chunk, args.regulations, i)
                futures.append(future)
            
            # Collect results
            chunk_results = []
            for future in futures:
                chunk_results.append(future.result())
        
        # Merge results
        merged_result = self.optimizer.merge_parallel_results(chunk_results)
        return merged_result
    
    def _process_chunk(self, chunk_data, regulations, chunk_id):
        """Process a data chunk (runs in separate process)"""
        try:
            # Initialize scanner in subprocess
            chunk_scanner = PIIScannerFacade()
            
            # Process the chunk
            result = chunk_scanner.analyze_schema_data(
                schema_data=chunk_data,
                regulations=regulations
            )
            
            return {
                'chunk_id': chunk_id,
                'result': result,
                'status': 'success'
            }
            
        except Exception as e:
            return {
                'chunk_id': chunk_id,
                'error': str(e),
                'status': 'error'
            }
    
    async def handle_batch(self, args) -> Dict:
        """Handle batch processing of multiple files"""
        input_path = Path(args.input_dir)
        output_path = Path(args.output_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_path}")
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Find files to process
        files = list(input_path.glob(args.pattern))
        
        if not files:
            print(f"No files found matching pattern: {args.pattern}")
            return {'processed': 0, 'files': []}
        
        print(f"📁 Found {len(files)} files to process")
        print(f"🔄 Using {args.workers} parallel workers")
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {}
            
            for file_path in files:
                future = executor.submit(self._process_batch_file, file_path, output_path, args)
                futures[future] = file_path
            
            # Collect results
            results = []
            for future in futures:
                file_path = futures[future]
                try:
                    result = future.result()
                    result['file'] = str(file_path)
                    results.append(result)
                    print(f"✅ Processed: {file_path.name}")
                except Exception as e:
                    print(f"❌ Failed: {file_path.name} - {e}")
                    results.append({
                        'file': str(file_path),
                        'status': 'error',
                        'error': str(e)
                    })
        
        batch_result = {
            'processed': len(results),
            'successful': len([r for r in results if r.get('status') != 'error']),
            'failed': len([r for r in results if r.get('status') == 'error']),
            'files': results
        }
        
        # Save batch summary
        summary_file = output_path / 'batch_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(batch_result, f, indent=2, default=str)
        
        print(f"📊 Batch processing complete:")
        print(f"   • Processed: {batch_result['processed']} files")
        print(f"   • Successful: {batch_result['successful']} files")
        print(f"   • Failed: {batch_result['failed']} files")
        print(f"   • Summary saved: {summary_file}")
        
        return batch_result
    
    def _process_batch_file(self, file_path: Path, output_path: Path, args) -> Dict:
        """Process a single file in batch mode"""
        try:
            result = self.scanner.analyze_schema_file(
                schema_file_path=str(file_path),
                regulations=args.regulations,
                enable_caching=True
            )
            
            # Save individual result
            output_file = output_path / f"{file_path.stem}_report.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            return {
                'status': 'success',
                'output_file': str(output_file),
                'findings': len(result.get('findings', []))
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def handle_benchmark(self, args) -> Dict:
        """Handle performance benchmarking"""
        print(f"🏃 Starting benchmark with {args.iterations} iterations")
        print(f"🔥 Warmup iterations: {args.warmup}")
        
        results = []
        
        # Warmup runs
        for i in range(args.warmup):
            print(f"Warmup {i+1}/{args.warmup}")
            self.scanner.analyze_schema_file(args.file, ['GDPR'])
        
        # Benchmark runs
        for i in range(args.iterations):
            print(f"Iteration {i+1}/{args.iterations}")
            
            start_time = time.time()
            result = self.scanner.analyze_schema_file(args.file, ['GDPR'])
            elapsed = time.time() - start_time
            
            results.append({
                'iteration': i + 1,
                'elapsed_time': elapsed,
                'findings': len(result.get('findings', []))
            })
        
        # Calculate statistics
        times = [r['elapsed_time'] for r in results]
        stats = {
            'iterations': args.iterations,
            'min_time': min(times),
            'max_time': max(times),
            'avg_time': sum(times) / len(times),
            'total_time': sum(times),
            'results': results
        }
        
        print(f"\n📊 Benchmark Results:")
        print(f"   • Average time: {stats['avg_time']:.3f}s")
        print(f"   • Min time: {stats['min_time']:.3f}s")
        print(f"   • Max time: {stats['max_time']:.3f}s")
        print(f"   • Total time: {stats['total_time']:.3f}s")
        
        return stats
    
    async def handle_cache(self, args) -> Dict:
        """Handle cache management"""
        cache_service = self.orchestrator.cache_service
        
        if args.clear:
            cache_service.clear_cache()
            print("🗑️  Cache cleared successfully")
        
        if args.stats:
            stats = cache_service.get_cache_stats()
            print("📊 Cache Statistics:")
            print(f"   • Total entries: {stats.get('total_entries', 0)}")
            print(f"   • Hit rate: {stats.get('hit_rate', 0):.2%}")
            print(f"   • Memory usage: {stats.get('memory_usage', 'N/A')}")
        
        if args.optimize:
            cache_service.optimize_cache()
            print("⚡ Cache optimized successfully")
        
        return {'status': 'success'}
    
    async def handle_server(self, args) -> None:
        """Handle server startup"""
        print(f"🚀 Starting PII Scanner Enterprise Server")
        print(f"   • Host: {args.host}")
        print(f"   • Port: {args.port}")
        print(f"   • Workers: {args.workers}")
        
        import uvicorn
        from backend.main import app
        
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            workers=args.workers,
            log_level="info"
        )
    
    async def _output_results(self, results: Dict, args):
        """Output results in requested format"""
        if args.output:
            output_path = Path(args.output)
            
            if args.format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
            elif args.format == 'csv':
                self._save_csv(results, output_path)
            elif args.format == 'html':
                self._save_html(results, output_path)
            
            if args.verbose:
                print(f"💾 Results saved to: {output_path}")
        
        elif args.verbose:
            # Print summary to console
            print("\n📋 Scan Summary:")
            findings = results.get('findings', [])
            print(f"   • Total fields analyzed: {results.get('total_fields', 0)}")
            print(f"   • PII/PHI fields found: {len(findings)}")
            
            if findings:
                print("\n🚨 High-risk fields:")
                for finding in findings[:5]:  # Show first 5
                    print(f"   • {finding.get('field_name')} ({finding.get('classification')})")
                
                if len(findings) > 5:
                    print(f"   ... and {len(findings) - 5} more")
    
    def _save_csv(self, results: Dict, output_path: Path):
        """Save results as CSV"""
        import csv
        
        findings = results.get('findings', [])
        
        with open(output_path, 'w', newline='') as f:
            if findings:
                writer = csv.DictWriter(f, fieldnames=findings[0].keys())
                writer.writeheader()
                writer.writerows(findings)
    
    def _save_html(self, results: Dict, output_path: Path):
        """Save results as HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PII Scanner Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
                .findings {{ margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                .high-risk {{ color: #dc3545; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>PII Scanner Report</h1>
                <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Total findings: {len(results.get('findings', []))}</p>
            </div>
            
            <div class="findings">
                <h2>Detected PII/PHI Fields</h2>
                <table>
                    <tr>
                        <th>Field Name</th>
                        <th>Table</th>
                        <th>Classification</th>
                        <th>Risk Level</th>
                    </tr>
        """
        
        for finding in results.get('findings', []):
            risk_class = 'high-risk' if finding.get('risk_level') == 'HIGH' else ''
            html_content += f"""
                    <tr>
                        <td class="{risk_class}">{finding.get('field_name', 'N/A')}</td>
                        <td>{finding.get('table_name', 'N/A')}</td>
                        <td>{finding.get('classification', 'N/A')}</td>
                        <td class="{risk_class}">{finding.get('risk_level', 'N/A')}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
    
    async def run(self):
        """Main CLI entry point"""
        parser = self.create_parser()
        args = parser.parse_args()
        
        if not args.command:
            parser.print_help()
            return
        
        try:
            if args.command == 'scan':
                await self.handle_scan(args)
            elif args.command == 'batch':
                await self.handle_batch(args)
            elif args.command == 'benchmark':
                await self.handle_benchmark(args)
            elif args.command == 'cache':
                await self.handle_cache(args)
            elif args.command == 'server':
                await self.handle_server(args)
                
        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user")
        except Exception as e:
            print(f"❌ Error: {e}")
            main_logger.error(f"CLI error: {e}")
            return 1
        
        return 0


if __name__ == '__main__':
    cli = EnterpriseCLI()
    exit_code = asyncio.run(cli.run())
    sys.exit(exit_code)