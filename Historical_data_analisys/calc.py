
def custom_round(num):
    num = num/10**6
    a = int(num)
    ostatok = num - a
    if ostatok<0.25: return a
    if ostatok<0.75: return a + 0.5
    return a+1