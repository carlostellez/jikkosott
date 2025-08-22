"""
Algorithm for identifying the top 10 most frequent customers within a specific time period.

This module implements an efficient solution for analyzing large datasets of e-commerce
transactions to identify frequent customers, with considerations for memory constraints
and scalability.

Problem Statement:
Given a large dataset of customer transactions from a local e-commerce platform,
each transaction includes a timestamp, customer ID, and purchase amount.
Design an algorithm to efficiently identify the top 10 most frequent customers
within a specific time period.

Time Complexity Analysis:
- Best Case: O(n) when using hash map with no collisions
- Average Case: O(n + k log k) where n is transactions and k is unique customers
- Worst Case: O(n log k) with heap operations

Space Complexity:
- O(k) where k is the number of unique customers in the time period
- For memory-constrained environments: O(1) with streaming approach
"""

import heapq
import random
from datetime import datetime, timedelta
from typing import List, Tuple, Generator
from dataclasses import dataclass
from collections import defaultdict, Counter
import csv
import os


@dataclass
class Transaction:
    """
    Represents a single customer transaction.
    
    Attributes:
        timestamp: When the transaction occurred
        customer_id: Unique identifier for the customer
        amount: Purchase amount in Colombian Pesos
    """
    timestamp: datetime
    customer_id: str
    amount: float


class FrequentCustomerAnalyzer:
    """
    Analyzer for identifying the most frequent customers in e-commerce data.
    
    This class provides multiple algorithms for different scenarios:
    1. In-memory analysis for datasets that fit in RAM
    2. Streaming analysis for memory-constrained environments
    3. Batch processing for extremely large datasets
    """
    
    def __init__(self):
        """Initialize the analyzer."""
        self.transactions = []
    
    def generate_data(self, num_transactions: int = 1000000) -> List[Transaction]:
        """
        Generate a large dataset of sample e-commerce transactions.
        
        This creates realistic transaction data for testing the algorithm
        with various customer behavior patterns.
        
        Args:
            num_transactions: Number of transactions to generate
            
        Returns:
            List of Transaction objects
            
        Time Complexity: O(n)
        Space Complexity: O(n)
        """
        print(f"Generating {num_transactions:,} sample transactions...")
        
        # Define customer segments with different frequency patterns
        vip_customers = [f"VIP_{i:06d}" for i in range(100)]  # 100 VIP customers (high frequency)
        regular_customers = [f"REG_{i:06d}" for i in range(5000)]  # 5K regular customers
        occasional_customers = [f"OCC_{i:06d}" for i in range(50000)]  # 50K occasional customers
        
        transactions = []
        base_date = datetime.now() - timedelta(days=365)
        
        for i in range(num_transactions):
            # Weighted random selection based on customer segments
            rand = random.random()
            if rand < 0.4:  # 40% from VIP customers (high frequency)
                customer_id = random.choice(vip_customers)
                amount = random.uniform(50000, 500000)  # Higher amounts
            elif rand < 0.8:  # 40% from regular customers
                customer_id = random.choice(regular_customers)
                amount = random.uniform(20000, 150000)  # Medium amounts
            else:  # 20% from occasional customers
                customer_id = random.choice(occasional_customers)
                amount = random.uniform(10000, 80000)  # Lower amounts
            
            # Generate timestamp within the last year
            days_offset = random.randint(0, 364)
            hours_offset = random.randint(0, 23)
            minutes_offset = random.randint(0, 59)
            
            timestamp = base_date + timedelta(
                days=days_offset,
                hours=hours_offset,
                minutes=minutes_offset
            )
            
            transactions.append(Transaction(timestamp, customer_id, amount))
            
            if (i + 1) % 100000 == 0:
                print(f"Generated {i + 1:,} transactions...")
        
        print("Sample data generation completed!")
        return transactions
    
    def find_frequent_customers_hash_map(
        self,
        transactions: List[Transaction],
        start_date: datetime,
        end_date: datetime,
        top_k: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Find top K frequent customers using hash map approach.
        
        This is the most efficient approach for datasets that fit in memory.
        Uses a hash map to count customer frequencies and a min-heap to
        maintain the top K customers.
        
        Args:
            transactions: List of all transactions
            start_date: Start of time period
            end_date: End of time period
            top_k: Number of top customers to return
            
        Returns:
            List of tuples (customer_id, frequency) sorted by frequency desc
            
        Time Complexity: O(n + k log k) where n = transactions, k = unique customers
        Space Complexity: O(k) where k = unique customers in time period
        """
        print(f"Analyzing {len(transactions):,} transactions with hash map approach...")
        
        # Filter transactions by time period and count frequencies
        customer_counts = defaultdict(int)
        filtered_count = 0
        
        for transaction in transactions:
            if start_date <= transaction.timestamp <= end_date:
                customer_counts[transaction.customer_id] += 1
                filtered_count += 1
        
        print(f"Filtered to {filtered_count:,} transactions in time period")
        print(f"Found {len(customer_counts):,} unique customers")
        
        # Use min-heap to efficiently find top K customers
        # We maintain a heap of size K to avoid sorting all customers
        min_heap = []
        
        for customer_id, frequency in customer_counts.items():
            if len(min_heap) < top_k:
                heapq.heappush(min_heap, (frequency, customer_id))
            elif frequency > min_heap[0][0]:
                heapq.heapreplace(min_heap, (frequency, customer_id))
        
        # Extract results and sort in descending order
        result = [(customer_id, frequency) for frequency, customer_id in min_heap]
        result.sort(key=lambda x: x[1], reverse=True)
        
        return result
    
    def find_frequent_customers_streaming(
        self,
        transaction_generator: Generator[Transaction, None, None],
        start_date: datetime,
        end_date: datetime,
        top_k: int = 10,
        memory_limit_customers: int = 100000
    ) -> List[Tuple[str, int]]:
        """
        Find top K frequent customers using streaming approach.
        
        This approach is designed for memory-constrained environments where
        the full dataset cannot fit in memory. It processes transactions
        one at a time and maintains only the necessary state.
        
        Args:
            transaction_generator: Generator yielding transactions one by one
            start_date: Start of time period
            end_date: End of time period
            top_k: Number of top customers to return
            memory_limit_customers: Maximum customers to keep in memory
            
        Returns:
            List of tuples (customer_id, frequency) sorted by frequency desc
            
        Time Complexity: O(n log k) where n = transactions, k = top_k
        Space Complexity: O(min(unique_customers, memory_limit))
        """
        print("Analyzing transactions with streaming approach...")
        
        customer_counts = {}
        min_heap = []  # Min-heap for top K customers
        processed_count = 0
        filtered_count = 0
        
        for transaction in transaction_generator:
            processed_count += 1
            
            if processed_count % 100000 == 0:
                print(f"Processed {processed_count:,} transactions...")
            
            # Skip transactions outside time period
            if not (start_date <= transaction.timestamp <= end_date):
                continue
            
            filtered_count += 1
            customer_id = transaction.customer_id
            
            # Update customer count
            if customer_id in customer_counts:
                old_count = customer_counts[customer_id]
                new_count = old_count + 1
                customer_counts[customer_id] = new_count
                
                # Update heap if this customer is in top K
                for i, (count, cust_id) in enumerate(min_heap):
                    if cust_id == customer_id:
                        min_heap[i] = (new_count, customer_id)
                        heapq.heapify(min_heap)
                        break
            else:
                customer_counts[customer_id] = 1
                
                # Add to heap if we have space or if frequency is high enough
                if len(min_heap) < top_k:
                    heapq.heappush(min_heap, (1, customer_id))
                elif 1 > min_heap[0][0]:
                    heapq.heapreplace(min_heap, (1, customer_id))
            
            # Memory management: remove least frequent customers if memory limit exceeded
            if len(customer_counts) > memory_limit_customers:
                # Remove customers not in top K with count = 1
                customers_to_remove = [
                    cust_id for cust_id, count in customer_counts.items()
                    if count == 1 and (count, cust_id) not in min_heap
                ]
                
                for cust_id in customers_to_remove[:len(customer_counts) - memory_limit_customers]:
                    del customer_counts[cust_id]
        
        print(f"Processed {processed_count:,} total transactions")
        print(f"Filtered to {filtered_count:,} transactions in time period")
        
        # Extract and sort results
        result = [(customer_id, frequency) for frequency, customer_id in min_heap]
        result.sort(key=lambda x: x[1], reverse=True)
        
        return result
    
    def find_frequent_customers_external_sort(
        self,
        transactions_file: str,
        start_date: datetime,
        end_date: datetime,
        top_k: int = 10,
        chunk_size: int = 100000
    ) -> List[Tuple[str, int]]:
        """
        Find top K frequent customers using external sorting for very large datasets.
        
        This approach handles datasets that exceed available memory by using
        external sorting techniques with temporary files.
        
        Args:
            transactions_file: Path to CSV file containing transactions
            start_date: Start of time period
            end_date: End of time period
            top_k: Number of top customers to return
            chunk_size: Number of transactions to process per chunk
            
        Returns:
            List of tuples (customer_id, frequency) sorted by frequency desc
            
        Time Complexity: O(n log n) due to external sorting
        Space Complexity: O(chunk_size)
        """
        print(f"Processing large dataset with external sorting (chunk size: {chunk_size:,})...")
        
        temp_files = []
        chunk_number = 0
        
        try:
            # Phase 1: Process data in chunks and create sorted temporary files
            with open(transactions_file, 'r') as file:
                reader = csv.DictReader(file)
                chunk_data = []
                
                for row in reader:
                    timestamp = datetime.fromisoformat(row['timestamp'])
                    
                    # Skip transactions outside time period
                    if not (start_date <= timestamp <= end_date):
                        continue
                    
                    chunk_data.append(row['customer_id'])
                    
                    if len(chunk_data) >= chunk_size:
                        # Process chunk and write to temporary file
                        chunk_counts = Counter(chunk_data)
                        temp_file = f"temp_chunk_{chunk_number}.txt"
                        temp_files.append(temp_file)
                        
                        with open(temp_file, 'w') as temp:
                            for customer_id, count in sorted(chunk_counts.items()):
                                temp.write(f"{customer_id},{count}\\n")
                        
                        chunk_data = []
                        chunk_number += 1
                        print(f"Processed chunk {chunk_number}")
                
                # Process final chunk
                if chunk_data:
                    chunk_counts = Counter(chunk_data)
                    temp_file = f"temp_chunk_{chunk_number}.txt"
                    temp_files.append(temp_file)
                    
                    with open(temp_file, 'w') as temp:
                        for customer_id, count in sorted(chunk_counts.items()):
                            temp.write(f"{customer_id},{count}\\n")
            
            # Phase 2: Merge temporary files and find top K
            print(f"Merging {len(temp_files)} temporary files...")
            customer_totals = defaultdict(int)
            
            for temp_file in temp_files:
                with open(temp_file, 'r') as file:
                    for line in file:
                        customer_id, count = line.strip().split(',')
                        customer_totals[customer_id] += int(count)
            
            # Find top K customers
            min_heap = []
            for customer_id, frequency in customer_totals.items():
                if len(min_heap) < top_k:
                    heapq.heappush(min_heap, (frequency, customer_id))
                elif frequency > min_heap[0][0]:
                    heapq.heapreplace(min_heap, (frequency, customer_id))
            
            result = [(customer_id, frequency) for frequency, customer_id in min_heap]
            result.sort(key=lambda x: x[1], reverse=True)
            
            return result
        
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    
    def benchmark_algorithms(self, size: int = 500000):
        """
        Benchmark different algorithms with various dataset sizes.
        
        Args:
            size: Size of the sample dataset to generate
        """
        import time
        
        print(f"\\n{'='*60}")
        print("FREQUENT CUSTOMERS ALGORITHM BENCHMARK")
        print(f"{'='*60}")
        
        # Generate sample data
        transactions = self.generate_data(size)
        
        # Define time period (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print(f"\\nAnalyzing time period: {start_date.date()} to {end_date.date()}")
        
        # Benchmark hash map approach
        print(f"\\n{'-'*40}")
        print("1. HASH MAP APPROACH (In-Memory)")
        print(f"{'-'*40}")
        
        start_time = time.time()
        hash_result = self.find_frequent_customers_hash_map(
            transactions, start_date, end_date
        )
        hash_time = time.time() - start_time
        
        print(f"Execution time: {hash_time:.3f} seconds")
        print("Top 10 most frequent customers:")
        for i, (customer_id, frequency) in enumerate(hash_result, 1):
            print(f"  {i:2d}. {customer_id}: {frequency:,} transactions")
        
        # Benchmark streaming approach
        print(f"\\n{'-'*40}")
        print("2. STREAMING APPROACH (Memory-Constrained)")
        print(f"{'-'*40}")
        
        def transaction_generator():
            for transaction in transactions:
                yield transaction
        
        start_time = time.time()
        streaming_result = self.find_frequent_customers_streaming(
            transaction_generator(), start_date, end_date
        )
        streaming_time = time.time() - start_time
        
        print(f"Execution time: {streaming_time:.3f} seconds")
        print("Top 10 most frequent customers:")
        for i, (customer_id, frequency) in enumerate(streaming_result, 1):
            print(f"  {i:2d}. {customer_id}: {frequency:,} transactions")
        
        # Verify results match
        print(f"\\n{'-'*40}")
        print("ALGORITHM VERIFICATION")
        print(f"{'-'*40}")
        
        results_match = hash_result == streaming_result
        print(f"Hash Map vs Streaming results match: {results_match}")
        
        if not results_match:
            print("WARNING: Results don't match! Investigating...")
            print("Hash Map result:", hash_result[:5])
            print("Streaming result:", streaming_result[:5])
        
        # Performance analysis
        print(f"\\n{'-'*40}")
        print("PERFORMANCE ANALYSIS")
        print(f"{'-'*40}")
        print(f"Dataset size: {len(transactions):,} transactions")
        print(f"Hash Map approach: {hash_time:.3f}s")
        print(f"Streaming approach: {streaming_time:.3f}s")
        print(f"Performance ratio: {streaming_time/hash_time:.2f}x")
        
        # Memory usage estimates
        unique_customers = len(set(t.customer_id for t in transactions 
                                 if start_date <= t.timestamp <= end_date))
        hash_memory_mb = (len(transactions) * 64 + unique_customers * 128) / (1024 * 1024)
        streaming_memory_mb = (unique_customers * 64) / (1024 * 1024)
        
        print(f"\\nMemory usage estimates:")
        print(f"Hash Map approach: ~{hash_memory_mb:.1f} MB")
        print(f"Streaming approach: ~{streaming_memory_mb:.1f} MB")
        print(f"Memory savings: {(1 - streaming_memory_mb/hash_memory_mb)*100:.1f}%")


def main():
    """
    Demonstrate the frequent customers algorithm with different approaches.
    """
    analyzer = FrequentCustomerAnalyzer()
    
    # Run comprehensive benchmark
    analyzer.benchmark_algorithms(size=1000000)
    
    # Additional complexity analysis
    print(f"\\n{'='*60}")
    print("COMPLEXITY ANALYSIS SUMMARY")
    print(f"{'='*60}")
    
    print("""
    ALGORITHM APPROACHES:
    
    1. Hash Map Approach (In-Memory):
       - Time Complexity: O(n + k log k)
         * n = number of transactions
         * k = number of unique customers
       - Space Complexity: O(k)
       - Best for: Datasets that fit in memory
       - Pros: Fastest execution, simple implementation
       - Cons: High memory usage for large datasets
    
    2. Streaming Approach (Memory-Constrained):
       - Time Complexity: O(n log k)
       - Space Complexity: O(min(k, memory_limit))
       - Best for: Large datasets with memory constraints
       - Pros: Controlled memory usage, handles any dataset size
       - Cons: Slightly slower due to heap operations
    
    3. External Sort Approach (Very Large Datasets):
       - Time Complexity: O(n log n)
       - Space Complexity: O(chunk_size)
       - Best for: Datasets exceeding available memory
       - Pros: Handles extremely large datasets
       - Cons: Slowest due to I/O operations
    
    RECOMMENDATIONS:
    - Use Hash Map for datasets < 1GB
    - Use Streaming for datasets 1GB - 100GB  
    - Use External Sort for datasets > 100GB
    
    SCALABILITY CONSIDERATIONS:
    - For real-time analysis: Implement sliding window with streaming
    - For distributed systems: Use MapReduce or Spark
    - For time series: Consider approximate algorithms (Count-Min Sketch)
    """)


if __name__ == "__main__":
    main()
