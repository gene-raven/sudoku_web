def borders(i, j):
    """Add class border-top for every third row. Add class border-left to every third column"""
    s = ""
    if not i % 3 and i:
        s += " border-top"
    if not j % 3 and j:
        s += " border-left"
    return s

def x_borders(i, j):
    s = borders(i, j)
    if i == j or i + j == 8: s += " diagonal"
    return s