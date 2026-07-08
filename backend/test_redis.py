import redis

try:
    r = redis.Redis(
        host="localhost",
        port=6379,
        db=1,
        decode_responses=True
    )

    print("Ping:", r.ping())

    r.set("test_key", "Hello Redis")
    print("Value:", r.get("test_key"))

    print("Redis is working!")

except Exception as e:
    print("Redis Error:")
    print(e)