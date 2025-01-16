"""Cache example."""

from datetime import datetime, timedelta

from pepperpy.cache import CacheConfig, JsonDict, MemoryCache


def main() -> None:
    """Run cache example."""
    # Create cache with configuration
    config = CacheConfig(ttl=60, max_size=100)
    cache = MemoryCache(config)

    # Set value with expiration and metadata
    expires_at = datetime.now() + timedelta(minutes=5)
    metadata: JsonDict = {"source": "example"}
    entry = cache.set("key1", "value1", expires_at=expires_at, metadata=metadata)
    print(f"Set value: {entry}")

    # Get value
    maybe_entry = cache.get("key1")
    if maybe_entry:
        print(f"Got value: {maybe_entry}")
    else:
        print("Value not found")

    # Delete value
    maybe_entry = cache.delete("key1")
    if maybe_entry:
        print(f"Deleted value: {maybe_entry}")
    else:
        print("Value not found")

    # Clear cache
    cache.clear()
    print("Cache cleared")


if __name__ == "__main__":
    main()
