from multiprocessing import cpu_count

import argon2

from app.core.config import settings

_hasher = argon2.PasswordHasher(
    time_cost=settings.HASH_ITERATION,
    memory_cost=settings.HASH_RAM_USAGE,
    parallelism=int(
        max(
            1,
            min(
                cpu_count() - settings.HASH_PRESERVE_CPU_CORE,
                round(cpu_count() * settings.HASH_THREADS_PER_CORE),
            ),
        )
    ),
    hash_len=settings.HASH_LENGTH,
    salt_len=settings.HASH_SALT_LENGTH,
    encoding="utf-8",
    type={
        "argon2d": argon2.Type.D,
        "argon2i": argon2.Type.I,
        "argon2id": argon2.Type.ID,
    }[settings.HASH_TYPE.strip().lower()],
)


def hash(password: str) -> str:
    return str(
        _hasher.hash(
            str(password, "utf-8") if hasattr(password, "decode") else str(password)
        )
    )


def verify(hash: str, password: str) -> bool:
    try:
        return bool(
            _hasher.verify(
                hash=str(hash, "utf-8") if hasattr(hash, "decode") else str(hash),
                password=str(password, "utf-8")
                if hasattr(password, "decode")
                else str(password),
            )
        )
    except (
        argon2.exceptions.VerifyMismatchError,
        argon2.exceptions.VerificationError,
        argon2.exceptions.InvalidHash,
    ):
        return False


def is_hash_deprecated(hash: str) -> bool:
    try:
        return bool(
            _hasher.check_needs_rehash(
                str(hash, "utf-8") if hasattr(hash, "decode") else str(hash)
            )
        )
    except argon2.exceptions.InvalidHash:
        return False


__all__ = ["hash", "verify", "is_hash_deprecated"]
