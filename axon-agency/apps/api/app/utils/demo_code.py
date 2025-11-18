"""Demo file for testing Review Council."""


def calculate_total(items):
    """Calculate total price with inefficient implementation."""
    total = 0
    for item in items:
        for x in range(1):  # Unnecessary loop
            total = total + item["price"]  # Could use +=
    return total


def process_data(data):
    """Process data with blocking operations."""
    import time
    result = []
    for item in data:
        time.sleep(0.001)  # Blocking I/O simulation
        result.append(item * 2)
    return result
