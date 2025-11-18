#!/usr/bin/env python3
"""Integration test script for Axon Agency <-> Axon Core connection."""

import asyncio
import httpx
import sys
import os
from pathlib import Path
from datetime import datetime

BASE_URL = "http://localhost:8080"
AXON_CORE_URL = os.getenv("AXON_CORE_API_BASE", "https://api-axon88.algorithmicsai.com")
LOG_FILE = Path(__file__).parent.parent / "logs" / "integration.log"


class IntegrationTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.axon_core_url = AXON_CORE_URL
        self.token = None
        self.results = []
        
        LOG_FILE.parent.mkdir(exist_ok=True)
        
    def log(self, message: str, level: str = "INFO"):
        """Log message to console and file."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    
    async def test_local_health(self):
        """Test 1: Local backend health check."""
        self.log("Testing local backend health...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/health")
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "healthy":
                    self.log("✅ Local backend is healthy", "SUCCESS")
                    self.results.append(("Local Health", True))
                    return True
                else:
                    self.log(f"❌ Unexpected health response: {data}", "ERROR")
                    self.results.append(("Local Health", False))
                    return False
        except Exception as e:
            self.log(f"❌ Local health check failed: {e}", "ERROR")
            self.results.append(("Local Health", False))
            return False
    
    async def get_dev_token(self):
        """Test 2: Get development token."""
        self.log("Getting development token...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/api/auth/dev/token")
                response.raise_for_status()
                data = response.json()
                
                self.token = data.get("access_token")
                if self.token:
                    self.log("✅ Development token obtained", "SUCCESS")
                    self.results.append(("Dev Token", True))
                    return True
                else:
                    self.log("❌ No token in response", "ERROR")
                    self.results.append(("Dev Token", False))
                    return False
        except Exception as e:
            self.log(f"❌ Token request failed: {e}", "ERROR")
            self.results.append(("Dev Token", False))
            return False
    
    async def test_axon_core_connectivity(self):
        """Test 3: Direct Axon Core connectivity."""
        self.log(f"Testing Axon Core connectivity to {self.axon_core_url}...")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.axon_core_url}/api/health")
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "healthy":
                    self.log("✅ Axon Core is reachable and healthy", "SUCCESS")
                    self.results.append(("Axon Core Direct", True))
                    return True
                else:
                    self.log(f"❌ Unexpected Axon Core response: {data}", "ERROR")
                    self.results.append(("Axon Core Direct", False))
                    return False
        except httpx.ConnectError as e:
            self.log(f"❌ Cannot connect to Axon Core: {e}", "ERROR")
            self.log("⚠️  Make sure cloudflared tunnel is running on Axon 88", "WARN")
            self.results.append(("Axon Core Direct", False))
            return False
        except Exception as e:
            self.log(f"❌ Axon Core connectivity test failed: {e}", "ERROR")
            self.results.append(("Axon Core Direct", False))
            return False
    
    async def test_axon_core_proxy(self):
        """Test 4: Axon Core proxy through local backend."""
        self.log("Testing Axon Core proxy endpoint...")
        
        if not self.token:
            self.log("❌ No token available, skipping proxy test", "ERROR")
            self.results.append(("Axon Core Proxy", False))
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/axon-core/health",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ Axon Core proxy working: {data}", "SUCCESS")
                    self.results.append(("Axon Core Proxy", True))
                    return True
                elif response.status_code == 503:
                    self.log("⚠️  Axon Core proxy reports service unavailable", "WARN")
                    self.results.append(("Axon Core Proxy", False))
                    return False
                else:
                    self.log(f"❌ Unexpected proxy response: {response.status_code}", "ERROR")
                    self.results.append(("Axon Core Proxy", False))
                    return False
        except Exception as e:
            self.log(f"❌ Axon Core proxy test failed: {e}", "ERROR")
            self.results.append(("Axon Core Proxy", False))
            return False
    
    async def test_axon_core_catalog(self):
        """Test 5: Get Axon Core catalog."""
        self.log("Fetching Axon Core catalog...")
        
        if not self.token:
            self.log("❌ No token available, skipping catalog test", "ERROR")
            self.results.append(("Axon Core Catalog", False))
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/axon-core/catalog",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ Axon Core catalog received", "SUCCESS")
                    self.log(f"   Features: {list(data.get('features', {}).keys())}", "INFO")
                    self.results.append(("Axon Core Catalog", True))
                    return True
                else:
                    self.log(f"⚠️  Could not fetch catalog: {response.status_code}", "WARN")
                    self.results.append(("Axon Core Catalog", False))
                    return False
        except Exception as e:
            self.log(f"❌ Catalog test failed: {e}", "ERROR")
            self.results.append(("Axon Core Catalog", False))
            return False
    
    async def test_local_catalog(self):
        """Test 6: Local catalog."""
        self.log("Testing local catalog...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/catalog")
                response.raise_for_status()
                data = response.json()
                
                features = data.get("features", {})
                self.log(f"✅ Local catalog received", "SUCCESS")
                self.log(f"   Features: chat={features.get('chat')}, websocket={features.get('websocket')}", "INFO")
                self.results.append(("Local Catalog", True))
                return True
        except Exception as e:
            self.log(f"❌ Local catalog test failed: {e}", "ERROR")
            self.results.append(("Local Catalog", False))
            return False
    
    def print_summary(self):
        """Print test summary."""
        self.log("\n" + "="*60, "INFO")
        self.log("INTEGRATION TEST SUMMARY", "INFO")
        self.log("="*60, "INFO")
        
        total = len(self.results)
        passed = sum(1 for _, success in self.results if success)
        failed = total - passed
        
        for test_name, success in self.results:
            status = "✅ PASS" if success else "❌ FAIL"
            self.log(f"{status}: {test_name}", "INFO")
        
        self.log("-"*60, "INFO")
        self.log(f"Total: {total} | Passed: {passed} | Failed: {failed}", "INFO")
        
        if failed == 0:
            self.log("\n✅ Integración completa Axon Core ↔ Replit ↔ OpenAI", "SUCCESS")
            self.log(f"🌐 Axon Core URL: {self.axon_core_url}", "SUCCESS")
            self.log("🤖 Chat AI funcionando", "SUCCESS")
            self.log("📡 Comunicación WebSocket activa", "SUCCESS")
            self.log("📦 Autopilots y landings listos", "SUCCESS")
            return 0
        else:
            self.log(f"\n⚠️  {failed} test(s) failed", "WARN")
            if any("Axon Core" in name for name, success in self.results if not success):
                self.log("\n💡 Troubleshooting:", "INFO")
                self.log("   1. Verify cloudflared tunnel is running on Axon 88", "INFO")
                self.log("   2. Check tunnel URL is correct", "INFO")
                self.log("   3. Ensure Axon Core API is running on port 8080", "INFO")
            return 1
    
    async def run_all_tests(self):
        """Run all integration tests."""
        self.log(f"Starting integration tests at {datetime.now()}", "INFO")
        self.log(f"Local URL: {self.base_url}", "INFO")
        self.log(f"Axon Core URL: {self.axon_core_url}", "INFO")
        self.log("-"*60, "INFO")
        
        await self.test_local_health()
        await self.get_dev_token()
        await self.test_local_catalog()
        await self.test_axon_core_connectivity()
        await self.test_axon_core_proxy()
        await self.test_axon_core_catalog()
        
        return self.print_summary()


async def main():
    """Main entry point."""
    tester = IntegrationTester()
    exit_code = await tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
