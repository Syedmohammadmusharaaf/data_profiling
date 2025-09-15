"""
Performance Optimizer for Enterprise PII Scanner
Provides intelligent optimizations for large dataset processing
"""

import os
import time
import psutil
import threading
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from collections import defaultdict
import cachetools
import pickle
import hashlib

from pii_scanner_poc.utils.logging_config import main_logger


@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""
    start_time: float
    end_time: Optional[float] = None
    memory_usage_mb: float = 0
    cpu_usage_percent: float = 0
    cache_hits: int = 0
    cache_misses: int = 0
    parallel_tasks: int = 0
    
    @property
    def elapsed_time(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
    
    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0


class PerformanceOptimizer:
    """Enterprise-grade performance optimizer for PII scanning"""
    
    def __init__(self):
        self.fast_mode = False
        self.streaming_mode = False
        self.intelligent_caching = False
        
        # Performance monitoring
        self.metrics = PerformanceMetrics(start_time=time.time())
        self.monitor_thread = None
        self.monitoring_active = False
        
        # Caching system
        self.result_cache = cachetools.TTLCache(maxsize=1000, ttl=3600)  # 1 hour TTL
        self.schema_fingerprint_cache = cachetools.LRUCache(maxsize=500)
        
        # Parallel processing configuration
        self.cpu_count = mp.cpu_count()
        self.optimal_workers = min(self.cpu_count, 8)  # Cap at 8 for memory efficiency
        self.chunk_size_calculator = ChunkSizeCalculator()
        
        # Memory management
        self.memory_threshold_mb = 1024  # 1GB threshold
        self.memory_monitor = MemoryMonitor()
        
        main_logger.info(f"Performance optimizer initialized with {self.cpu_count} CPUs")
    
    def enable_fast_mode(self):
        """Enable fast mode optimizations"""
        self.fast_mode = True
        
        # Fast mode optimizations
        self.result_cache.ttl = 7200  # Extend cache TTL
        self.optimal_workers = min(self.cpu_count * 2, 16)  # More aggressive parallelism
        
        main_logger.info("Fast mode enabled - using aggressive optimizations")
    
    def enable_streaming_mode(self):
        """Enable streaming mode for large files"""
        self.streaming_mode = True
        main_logger.info("Streaming mode enabled for large dataset processing")
    
    def enable_intelligent_caching(self):
        """Enable intelligent caching system"""
        self.intelligent_caching = True
        main_logger.info("Intelligent caching enabled")
    
    def start_monitoring(self):
        """Start performance monitoring in background thread"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_performance, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        self.metrics.end_time = time.time()
    
    def _monitor_performance(self):
        """Background performance monitoring"""
        while self.monitoring_active:
            try:
                # CPU and memory monitoring
                process = psutil.Process()
                self.metrics.cpu_usage_percent = process.cpu_percent()
                self.metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
                
                # Memory pressure detection
                if self.metrics.memory_usage_mb > self.memory_threshold_mb:
                    self._handle_memory_pressure()
                
                time.sleep(1)  # Monitor every second
                
            except Exception as e:
                main_logger.warning(f"Performance monitoring error: {e}")
    
    def _handle_memory_pressure(self):
        """Handle high memory usage"""
        main_logger.warning(f"High memory usage detected: {self.metrics.memory_usage_mb:.1f}MB")
        
        # Clear caches to free memory
        cache_size_before = len(self.result_cache)
        self.result_cache.clear()
        self.schema_fingerprint_cache.clear()
        
        main_logger.info(f"Cleared {cache_size_before} cache entries to free memory")
    
    def create_parallel_chunks(self, data: List[Dict], num_workers: int) -> List[List[Dict]]:
        """Create optimally sized chunks for parallel processing"""
        if not data:
            return []
        
        # Calculate optimal chunk size
        chunk_size = self.chunk_size_calculator.calculate_optimal_size(
            total_items=len(data),
            num_workers=num_workers,
            item_complexity=self._estimate_item_complexity(data[0]) if data else 1
        )
        
        chunks = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            chunks.append(chunk)
        
        main_logger.info(f"Created {len(chunks)} chunks of ~{chunk_size} items each for {num_workers} workers")
        return chunks
    
    def _estimate_item_complexity(self, item: Dict) -> int:
        """Estimate complexity score for an item (1-10 scale)"""
        complexity = 1
        
        # More columns = higher complexity
        if 'columns' in item:
            complexity += min(len(item['columns']) // 10, 5)
        
        # Nested structures add complexity
        if isinstance(item, dict):
            complexity += min(len(str(item)) // 1000, 3)
        
        return min(complexity, 10)
    
    def merge_parallel_results(self, chunk_results: List[Dict]) -> Dict:
        """Merge results from parallel processing"""
        merged = {
            'findings': [],
            'summary': {'total_tables': 0, 'total_columns': 0, 'total_findings': 0},
            'performance': {'parallel_chunks': len(chunk_results)},
            'metadata': {'processing_mode': 'parallel'}
        }
        
        for chunk_result in chunk_results:
            if chunk_result.get('status') == 'success':
                result_data = chunk_result.get('result', {})
                
                # Merge findings
                findings = result_data.get('findings', [])
                merged['findings'].extend(findings)
                
                # Merge summary statistics
                summary = result_data.get('summary', {})
                merged['summary']['total_tables'] += summary.get('total_tables', 0)
                merged['summary']['total_columns'] += summary.get('total_columns', 0)
                merged['summary']['total_findings'] += len(findings)
            
            else:
                main_logger.warning(f"Parallel chunk failed: {chunk_result.get('error')}")
        
        main_logger.info(f"Merged {len(chunk_results)} parallel results with {len(merged['findings'])} total findings")
        return merged
    
    def get_cache_key(self, schema_data: Any, regulations: List[str]) -> str:
        """Generate cache key for schema data"""
        # Create fingerprint of schema data and regulations
        schema_str = str(sorted(str(item) for item in schema_data))
        regulations_str = ''.join(sorted(regulations))
        combined = f"{schema_str}_{regulations_str}"
        
        return hashlib.md5(combined.encode()).hexdigest()
    
    def cache_result(self, cache_key: str, result: Dict):
        """Cache analysis result"""
        if self.intelligent_caching and cache_key:
            self.result_cache[cache_key] = result
            main_logger.debug(f"Cached result with key: {cache_key[:16]}...")
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached result"""
        if self.intelligent_caching and cache_key in self.result_cache:
            self.metrics.cache_hits += 1
            main_logger.debug(f"Cache hit for key: {cache_key[:16]}...")
            return self.result_cache[cache_key]
        
        self.metrics.cache_misses += 1
        return None
    
    def optimize_for_dataset_size(self, dataset_size: int) -> Dict[str, Any]:
        """Provide size-specific optimizations"""
        optimizations = {
            'batch_size': 100,
            'workers': self.optimal_workers,
            'memory_limit_mb': 512,
            'enable_streaming': False,
            'cache_strategy': 'standard'
        }
        
        if dataset_size < 1000:
            # Small dataset - optimize for speed
            optimizations.update({
                'batch_size': dataset_size,
                'workers': 2,
                'cache_strategy': 'aggressive'
            })
        
        elif dataset_size < 10000:
            # Medium dataset - balanced approach
            optimizations.update({
                'batch_size': 500,
                'workers': min(self.optimal_workers, 4),
                'cache_strategy': 'intelligent'
            })
        
        else:
            # Large dataset - optimize for memory efficiency
            optimizations.update({
                'batch_size': 200,
                'workers': self.optimal_workers,
                'memory_limit_mb': 1024,
                'enable_streaming': True,
                'cache_strategy': 'conservative'
            })
        
        main_logger.info(f"Optimizations for dataset size {dataset_size}: {optimizations}")
        return optimizations
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        return {
            'execution_time': self.metrics.elapsed_time,
            'peak_memory_mb': self.metrics.memory_usage_mb,
            'avg_cpu_usage': self.metrics.cpu_usage_percent,
            'cache_performance': {
                'hit_rate': self.metrics.cache_hit_rate,
                'total_hits': self.metrics.cache_hits,
                'total_misses': self.metrics.cache_misses
            },
            'parallel_processing': {
                'enabled': self.metrics.parallel_tasks > 0,
                'tasks': self.metrics.parallel_tasks,
                'optimal_workers': self.optimal_workers
            },
            'optimizations': {
                'fast_mode': self.fast_mode,
                'streaming_mode': self.streaming_mode,
                'intelligent_caching': self.intelligent_caching
            }
        }


class ChunkSizeCalculator:
    """Calculates optimal chunk sizes for parallel processing"""
    
    def calculate_optimal_size(self, total_items: int, num_workers: int, item_complexity: int = 1) -> int:
        """Calculate optimal chunk size based on various factors"""
        
        # Base chunk size
        base_chunk_size = max(total_items // num_workers, 1)
        
        # Adjust for item complexity
        complexity_factor = max(1, item_complexity / 5)  # Scale down for complex items
        adjusted_size = int(base_chunk_size / complexity_factor)
        
        # Ensure reasonable bounds
        min_chunk_size = 1
        max_chunk_size = min(1000, total_items // 2) if total_items > 2 else total_items
        
        optimal_size = max(min_chunk_size, min(adjusted_size, max_chunk_size))
        
        return optimal_size


class MemoryMonitor:
    """Monitor and manage memory usage"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.peak_memory = 0
    
    def get_current_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        memory_mb = self.process.memory_info().rss / 1024 / 1024
        self.peak_memory = max(self.peak_memory, memory_mb)
        return memory_mb
    
    def get_system_memory_info(self) -> Dict[str, Any]:
        """Get system memory information"""
        virtual_memory = psutil.virtual_memory()
        return {
            'total_gb': virtual_memory.total / 1024 / 1024 / 1024,
            'available_gb': virtual_memory.available / 1024 / 1024 / 1024,
            'usage_percent': virtual_memory.percent,
            'free_gb': virtual_memory.free / 1024 / 1024 / 1024
        }
    
    def is_memory_pressure(self, threshold_percent: float = 85.0) -> bool:
        """Check if system is under memory pressure"""
        memory_info = self.get_system_memory_info()
        return memory_info['usage_percent'] > threshold_percent


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()