import asyncio
import time
import logging
from Trapdev import SMSBomber

# Configure logging for the test
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("StressTest")

async def test_concurrency():
    logger.info("Starting Concurrency Stress Test (Direct Class Usage)")
    
    # We'll measure how long it takes to run 3 batches of all services
    # with the new persistent session.
    
    start_time = time.time()
    
    async with SMSBomber() as bomber:
        logger.info("Triggering 3 batches of all services...")
        # Note: we use a real-looking but fake number for testing
        await bomber.execute_attack("09170000000", 3, ["all"])
        
        stats = bomber.get_stats()
        logger.info(f"Test Completed in {time.time() - start_time:.2f} seconds")
        logger.info(f"Stats: {stats}")

async def test_resource_leaks():
    logger.info("Starting Resource Leak Test...")
    # Triggering many small attacks to see if sessions are cleaned up
    for i in range(5):
        logger.info(f"Iteration {i+1}/5")
        async with SMSBomber() as bomber:
            await bomber.send_ezloan("09170000000")
    logger.info("Resource Leak Test (Manual Observation of Logs) Completed")

async def main():
    try:
        await test_concurrency()
        print("-" * 50)
        await test_resource_leaks()
    except Exception as e:
        logger.error(f"Stress test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
