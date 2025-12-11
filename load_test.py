import asyncio
import aiohttp
import time
from typing import List, Dict
import statistics
import json

class LoadTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        
        # Test queries
        self.queries = [
            "authentication login",
            "database connection",
            "error handling exception",
            "http request response",
            "file upload download",
            "user validation",
            "api endpoint",
            "cache implementation",
            "data processing",
            "security check",
            "unit test",
            "configuration settings",
            "logging debug",
            "async function",
            "json parsing",
            "form validation",
            "session management",
            "password encryption",
            "token authentication",
            "query optimization",
            "memory management",
            "thread pool",
            "connection pooling",
            "rate limiting",
            "middleware handler"
        ]
    
    async def make_request(self, session: aiohttp.ClientSession, query: str, request_id: int):
        """Make a single search request"""
        start_time = time.time()
        
        try:
            async with session.get(
                f"{self.base_url}/search",
                params={"q": query, "limit": 5},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                data = await response.json()
                elapsed = (time.time() - start_time) * 1000  # milliseconds
                
                return {
                    'request_id': request_id,
                    'query': query,
                    'status': response.status,
                    'time_ms': elapsed,
                    'success': response.status == 200,
                    'results_count': data.get('count', 0) if response.status == 200 else 0
                }
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            return {
                'request_id': request_id,
                'query': query,
                'status': 0,
                'time_ms': elapsed,
                'success': False,
                'error': str(e)
            }
    
    async def concurrent_batch(self, num_requests: int, concurrency: int):
        """Execute requests with specified concurrency"""
        print(f"\n🚀 Starting batch: {num_requests} requests with {concurrency} concurrent connections")
        
        connector = aiohttp.TCPConnector(limit=concurrency)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            
            for i in range(num_requests):
                query = self.queries[i % len(self.queries)]
                task = self.make_request(session, query, i)
                tasks.append(task)
            
            # Execute all requests concurrently
            results = await asyncio.gather(*tasks)
            self.results.extend(results)
            
        return results
    
    def analyze_results(self):
        """Analyze and print results"""
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        if not successful:
            print("❌ No successful requests!")
            return
        
        times = [r['time_ms'] for r in successful]
        
        print("\n" + "=" * 70)
        print("📊 LOAD TEST RESULTS")
        print("=" * 70)
        
        print(f"\n📈 Request Statistics:")
        print(f"  Total requests: {len(self.results)}")
        print(f"  Successful: {len(successful)} ({len(successful)/len(self.results)*100:.1f}%)")
        print(f"  Failed: {len(failed)} ({len(failed)/len(self.results)*100:.1f}%)")
        
        print(f"\n⚡ Response Time Statistics:")
        print(f"  Average: {statistics.mean(times):.2f}ms")
        print(f"  Median: {statistics.median(times):.2f}ms")
        print(f"  Min: {min(times):.2f}ms")
        print(f"  Max: {max(times):.2f}ms")
        print(f"  Std Dev: {statistics.stdev(times):.2f}ms")
        
        # Percentiles
        sorted_times = sorted(times)
        p50 = sorted_times[int(len(sorted_times) * 0.50)]
        p90 = sorted_times[int(len(sorted_times) * 0.90)]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99)]
        
        print(f"\n📊 Percentiles:")
        print(f"  P50 (median): {p50:.2f}ms")
        print(f"  P90: {p90:.2f}ms")
        print(f"  P95: {p95:.2f}ms")
        print(f"  P99: {p99:.2f}ms")
        
        # SLA compliance
        under_50ms = len([t for t in times if t < 50])
        under_100ms = len([t for t in times if t < 100])
        under_200ms = len([t for t in times if t < 200])
        
        print(f"\n🎯 SLA Compliance:")
        print(f"  < 50ms: {under_50ms} ({under_50ms/len(times)*100:.1f}%)")
        print(f"  < 100ms: {under_100ms} ({under_100ms/len(times)*100:.1f}%)")
        print(f"  < 200ms: {under_200ms} ({under_200ms/len(times)*100:.1f}%)")
        
        if failed:
            print(f"\n❌ Failed Requests:")
            for r in failed[:5]:  # Show first 5 failures
                print(f"  Request {r['request_id']}: {r.get('error', 'Unknown error')}")
        
        print("=" * 70)
    
    async def run_test(self, total_requests: int = 1000, concurrent_users: int = 100):
        """Run the complete load test"""
        print("=" * 70)
        print("🔥 CODE SEARCH ENGINE LOAD TEST")
        print("=" * 70)
        print(f"Target URL: {self.base_url}")
        print(f"Total Requests: {total_requests}")
        print(f"Concurrent Users: {concurrent_users}")
        print(f"Test Queries: {len(self.queries)} unique queries")
        print("=" * 70)
        
        # Check if server is up
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/") as response:
                    if response.status != 200:
                        print(f"❌ Server not responding properly (status: {response.status})")
                        return
                    print("✅ Server is up and responding")
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("Make sure your server is running with: python code_search_engine.py (then type 'api')")
            return
        
        start_time = time.time()
        
        # Run the load test
        await self.concurrent_batch(total_requests, concurrent_users)
        
        total_time = time.time() - start_time
        
        print(f"\n✅ Test completed in {total_time:.2f} seconds")
        print(f"📈 Throughput: {total_requests/total_time:.2f} requests/second")
        
        # Analyze results
        self.analyze_results()
        
        # Save results to file
        with open('load_test_results.json', 'w') as f:
            json.dump({
                'config': {
                    'total_requests': total_requests,
                    'concurrent_users': concurrent_users,
                    'total_time_seconds': total_time,
                    'throughput_rps': total_requests/total_time
                },
                'results': self.results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to load_test_results.json")

def main():
    """Main function"""
    print("\n🔍 Load Testing Tool for AI-Powered Code Search Engine\n")
    
    base_url = input("Enter API URL (default: http://localhost:5000): ").strip()
    if not base_url:
        base_url = "http://localhost:5000"
    
    try:
        total = int(input("Total requests (default: 1000): ").strip() or "1000")
        concurrent = int(input("Concurrent users (default: 100): ").strip() or "100")
    except ValueError:
        print("Invalid input, using defaults")
        total = 1000
        concurrent = 100
    
    tester = LoadTester(base_url)
    
    # Run the async test
    asyncio.run(tester.run_test(total, concurrent))

if __name__ == "__main__":
    main()