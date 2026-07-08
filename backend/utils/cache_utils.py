# utils/cache_utils.py
#
# Thin Redis caching layer for GET endpoints.
#
# Design:
# - get_redis() lazily builds a client from app.config["CACHE_REDIS_URL"].
# - cache_response() is a decorator for view functions that return
#   (jsonify(...), status) or just jsonify(...). It only caches 200s.
# - Cache keys are built from the route prefix + URL kwargs (e.g. drive_id)
#   + selected query-string params + (optionally) the JWT identity, so two
#   different companies/students never see each other's cached data.
# - All Redis errors are swallowed (logged) so a Redis outage degrades to
#   "no caching" instead of a 500.

import json
import hashlib
from functools import wraps

import redis
from flask import request, current_app, jsonify
from flask_jwt_extended import get_jwt_identity

_redis_client = None


def get_redis():
    global _redis_client
    if _redis_client is None:
        url = current_app.config.get("CACHE_REDIS_URL", "redis://localhost:6379/1")
        _redis_client = redis.StrictRedis.from_url(url, decode_responses=True)
    return _redis_client


def _make_key(prefix, *parts, **kwargs):
    raw = ":".join([prefix] + [str(p) for p in parts if p is not None])
    query_items = sorted((k, v) for k, v in kwargs.items() if v is not None)
    if query_items:
        query_str = "&".join(f"{k}={v}" for k, v in query_items)
        raw += ":" + hashlib.md5(query_str.encode()).hexdigest()
    return raw


def get_cache(key):
    print("GET CACHE:", key)
    try:
        value = get_redis().get(key)
        print("Redis value:", value)
        return json.loads(value) if value else None
    except Exception as e:
        print("Redis get error:", e)
        return None


def set_cache(key, value, ttl=None):
    ttl = ttl or current_app.config.get("CACHE_DEFAULT_TTL", 300)
    print("SET CACHE:", key)

    try:
        get_redis().setex(key, ttl, json.dumps(value, default=str))
        print("Cache stored successfully")
    except Exception as e:
        print("Redis set error:", e)

def delete_cache(key):
    try:
        get_redis().delete(key)
    except redis.exceptions.RedisError:
        current_app.logger.warning("Redis unavailable (delete_cache)")


def delete_pattern(pattern):
    """Invalidate every key matching a glob pattern, e.g. 'jobs:list:*'."""
    try:
        client = get_redis()
        keys = list(client.scan_iter(match=pattern, count=200))
        if keys:
            client.delete(*keys)
    except redis.exceptions.RedisError:
        current_app.logger.warning("Redis unavailable (delete_pattern)")


def cache_response(prefix, ttl=None, query_params=None, include_identity=False):
    """
    Decorator for GET view functions.

    prefix          - namespace for the key, e.g. "jobs:list"
    ttl             - seconds; falls back to CACHE_DEFAULT_TTL
    query_params    - list of request.args names to fold into the key
                       (e.g. ["company", "position", "skill"])
    include_identity- include the JWT identity in the key (use this when the
                       response differs per logged-in user, e.g. a company's
                       own job list). Must be placed so jwt_required() has
                       already run (see routes below).
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            query_kwargs = {}
            if query_params:
                for p in query_params:
                    query_kwargs[p] = request.args.get(p)

            identity_part = get_jwt_identity() if include_identity else None
            cache_key = _make_key(
                prefix, identity_part, *kwargs.values(), **query_kwargs
            )

            cached = get_cache(cache_key)
            if cached is not None:
                return jsonify(cached["body"]), cached["status"]

            result = fn(*args, **kwargs)
            response, status = result if isinstance(result, tuple) else (result, 200)

            if status == 200:
                try:
                    set_cache(cache_key, {"body": response.get_json(), "status": status}, ttl)
                except Exception:
                    current_app.logger.warning("cache_response: could not serialize response")

            return result
        return wrapper
    return decorator