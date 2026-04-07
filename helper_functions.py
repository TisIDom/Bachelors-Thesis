def lcm(n1: float, n2: float):
    return abs(n1*n2) / gcd(n1,n2)

def gcd(n1: float, n2: float):
    if n1 == 0 or n2 == 0:
        return n1+n2
    if n1 > n2:
        return gcd(n1%n2,n2)
    elif n1 <= n2:
        return gcd(n1,n2%n1)
    
    
    
    
    