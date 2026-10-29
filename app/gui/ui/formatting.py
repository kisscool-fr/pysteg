_KIB = 1024
_MIB = 1024 * 1024


def human_size(size: int) -> str:
    """Short, rounded file size: ``512 B``, ``24 KB``, ``2.4 MB``."""
    if size < _KIB:
        return f"{size} B"
    if size < _MIB:
        return f"{round(size / _KIB)} KB"
    return f"{size / _MIB:.1f} MB"


def plural(count: int, word: str) -> str:
    return f"{count:,} {word}" + ("" if count == 1 else "s")
