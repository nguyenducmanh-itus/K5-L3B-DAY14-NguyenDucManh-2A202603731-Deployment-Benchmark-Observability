"""
Rate limiting (tiêu chí 7).

Yêu cầu:
  • Mỗi API key tối đa RATE_LIMIT_PER_MINUTE request trong 60 giây (sliding window)
  • Vượt giới hạn → HTTP 429, nên kèm header Retry-After
  • State lưu trong Redis để mọi worker / instance dùng chung và vẫn còn sau khi
    restart agent (script chấm sẽ restart agent để kiểm tra)
"""


import math
import time
from fastapi import HTTPException
from redis.exceptions import RedisError
from app.config import settings
from app.redis_client import r

_SCRIPT = r"""
local k, now = KEYS[1], tonumber(ARGV[1])
redis.call('ZREMRANGEBYSCORE', k, '-inf', now - tonumber(ARGV[2]))
local count = redis.call('ZCARD', k)
if count >= tonumber(ARGV[3]) then
  local first = redis.call('ZRANGE', k, 0, 0, 'WITHSCORES')
  return {0, tonumber(first[2])}
end
redis.call('ZADD', k, now, ARGV[4])
redis.call('EXPIRE', k, 60)
return {1, 0}
"""


def check_rate_limit(key: str) -> None:
    now = int(time.time() * 1000)
    try:
        allowed, oldest = r.eval(_SCRIPT, 1, f"rate:{key}", now, 60_000,
                                 settings.rate_limit_per_minute, f"{now}:{time.time_ns()}")
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Rate-limit store unavailable") from exc
    if not int(allowed):
        retry = max(1, math.ceil((int(oldest) + 60_000 - now) / 1000))
        raise HTTPException(status_code=429, detail="Rate limit exceeded",
                            headers={"Retry-After": str(retry)})
