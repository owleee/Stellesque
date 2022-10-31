def GREY(n):
    "returns a grey value where 100 is white and 0 is black"
    n = (n / 100) * 255
    n = max(n, 0)
    n = min(n, 100)
    return (n, n, n)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 128, 0)
GREEN = (0, 255, 0)
CYAN = (0,255,255)