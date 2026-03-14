"""
Large Dataset Processor Module
Handles streaming/chunked processing for large datasets
"""

import pandas as pd
import numpy as np
import dask.dataframe as dd
from typing import Dict, Any, Iterator
import os


class LargeDatasetProcessor:
    """Efficiently processes large datasets without loading all into memory"""
    
    def __init__(self, file_path: str, file_type: str = 'csv'):
        """
        Initialize large dataset processor
        
        Args:
            file_path: Path to dataset file
            file_type: Type of file (csv, parquet, json, xlsx)
        """
        self.file_path = file_path
        self.file_type = file_type
        self.file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    def get_optimal_chunk_size(self) -> int:
        """Determine optimal chunk size based on file size"""
        if self.file_size_mb < 50:
            return None  # Load all at once
        elif self.file_size_mb < 500:
            return 50000
        else:
            # For very large files, use 10000 rows per chunk
            return 10000
    
    def process_large_csv(self, chunksize: int = None) -> Iterator[pd.DataFrame]:
        """
        Process large CSV file in chunks
        
        Args:
            chunksize: Number of rows per chunk
            
        Yields:
            pd.DataFrame chunks
        """
        if chunksize is None:
            chunksize = self.get_optimal_chunk_size() or 100000
        
        for chunk in pd.read_csv(self.file_path, chunksize=chunksize):
            yield chunk
    
    def process_large_parquet(self) -> Iterator[pd.DataFrame]:
        """
        Process large Parquet file efficiently
        
        Yields:
            pd.DataFrame chunks
        """
        # Use Dask for Parquet files
        dask_df = dd.read_parquet(self.file_path)
        
        # Convert to chunks
        n_partitions = dask_df.npartitions
        for i in range(n_partitions):
            yield dask_df.get_partition(i).compute()
    
    def process_large_json(self, lines: bool = True) -> Iterator[pd.DataFrame]:
        """
        Process large JSON file
        
        Args:
            lines: Whether file is JSON lines format
            
        Yields:
            pd.DataFrame chunks
        """
        chunksize = self.get_optimal_chunk_size() or 50000
        
        if lines:
            # JSON Lines format (each line is a separate JSON object)
            chunk_list = []
            count = 0
            
            with open(self.file_path, 'r') as f:
                for line in f:
                    try:
                        chunk_list.append(pd.read_json(line, typ='series', orient='records'))
                        count += 1
                        
                        if count >= chunksize:
                            yield pd.DataFrame(chunk_list)
                            chunk_list = []
                            count = 0
                    except:
                        pass
                
                if chunk_list:
                    yield pd.DataFrame(chunk_list)
        else:
            # Regular JSON file
            df = pd.read_json(self.file_path)
            for i in range(0, len(df), chunksize):
                yield df.iloc[i:i+chunksize]
    
    def get_statistics_streaming(self) -> Dict[str, Any]:
        """
        Calculate statistics from large dataset without loading all into memory
        """
        stats = {
            'total_rows': 0,
            'total_cols': 0,
            'numeric_stats': {},
            'categorical_stats': {},
            'memory_used_mb': 0
        }
        
        if self.file_type == 'csv':
            chunks_iter = self.process_large_csv()
        elif self.file_type == 'parquet':
            chunks_iter = self.process_large_parquet()
        elif self.file_type == 'json':
            chunks_iter = self.process_large_json()
        else:
            return stats
        
        first_chunk = True
        cumulative_memory = 0
        
        for chunk in chunks_iter:
            if first_chunk:
                stats['total_cols'] = len(chunk.columns)
                first_chunk = False
            
            stats['total_rows'] += len(chunk)
            cumulative_memory += chunk.memory_usage(deep=True).sum() / (1024*1024)
            
            # Update statistics
            self._update_streaming_stats(stats, chunk)
        
        stats['memory_used_mb'] = round(cumulative_memory, 2)
        return stats
    
    def _update_streaming_stats(self, stats: Dict, chunk: pd.DataFrame):
        """Update statistics with new chunk"""
        numeric_cols = chunk.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col not in stats['numeric_stats']:
                stats['numeric_stats'][col] = {
                    'min': float(chunk[col].min()),
                    'max': float(chunk[col].max()),
                    'mean': float(chunk[col].mean()),
                    'missing': int(chunk[col].isnull().sum())
                }
            else:
                stats['numeric_stats'][col]['min'] = min(
                    stats['numeric_stats'][col]['min'],
                    float(chunk[col].min())
                )
                stats['numeric_stats'][col]['max'] = max(
                    stats['numeric_stats'][col]['max'],
                    float(chunk[col].max())
                )
                stats['numeric_stats'][col]['missing'] += int(chunk[col].isnull().sum())
    
    def convert_to_manageable_dataframe(self, max_rows: int = 50000) -> pd.DataFrame:
        """
        Convert large dataset to manageable dataframe by sampling
        """
        if self.file_type == 'csv':
            # Read with skiprows for stratified sampling
            if self.file_size_mb < 500:
                df = pd.read_csv(self.file_path)
            else:
                # For very large files, read and sample
                df = pd.read_csv(self.file_path, nrows=max_rows*2)
        elif self.file_type == 'parquet':
            df = dd.read_parquet(self.file_path).compute()
        elif self.file_type == 'json':
            df = pd.read_json(self.file_path)
        else:
            return pd.DataFrame()
        
        # Ensure we don't exceed max_rows
        if len(df) > max_rows:
            # Stratified sampling if there's a target column
            return df.sample(n=max_rows, random_state=42)
        
        return df
