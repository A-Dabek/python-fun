from __future__ import print_function


def factorial(x):
    if x <= 1:
        return 1
    else:
        return x * factorial(x - 1)


def limited_factorial(x, limit):
    if x <= limit:
        return 1
    else:
        return x * limited_factorial(x - 1, limit)


def newton(n, p):
    if n < p or n < 0 or p < 0:
        return 0
    if p > n - p:
        return limited_factorial(n, p) / factorial(n - p)
    else:
        return limited_factorial(n, n - p) / factorial(p)


def alternating_newtonian_exponential_sum(xs, xf, n, verbose=True):
    sum = 0
    i = 0
    sign = 1
    nt = xf - xs
    strResult = 'anes\t'
    while xf >= xs:
        temp = sum
        sum += (xf ** n) * sign * newton(nt, i)
        if sign > 0:
            strResult += '+'
        else:
            strResult += '-'
        strResult += str(newton(nt,i)) + '*' + str(xf) + '^' + str(n) + ' '
        i += 1
        sign *= -1
        xf -= 1
    if verbose:
        print strResult
    return sum


def anes(xs, xf, n, verbose=True):
    return alternating_newtonian_exponential_sum(xs, xf, n, verbose)


def improved_even_anes(range, n, verbose=True):
    if range % 2 == 1:
        return 0
    else:
        sum = 0
        i = 0
        start = range / 2
        sign = 1
        nt = range
        strResult = 'improved_even_anes\t'
        while start >= -range / 2:
            temp = sum
            sum += (start ** n) * sign * newton(nt, i)
            if sign > 0:
                strResult += '+'
            else:
                strResult += 'i'
            strResult += str(newton(nt,i)) + '*' + str(start) + '^' + str(n) + ' '
            i += 1
            sign *= -1
            start -= 1
        if verbose:
            print strResult
        return sum


def alternating_newtonian_polynomial_sum(x, start, range, n, nt, verbose=True):
    sum = 0
    i = 0
    start -= 1
    sign = 1
    strResult = 'anps\t'
    while i < range:
        temp = sum
        sum += (x + start + range - i)**n * sign * newton(nt, i)
        if sign > 0:
            strResult += '+'
        else:
            strResult += '-'
        strResult += str(newton(nt, i)) + 'x(|' + str(x+start+range-i) + '|)^' + str(n) + ' '
        i += 1
        sign *= -1
    if verbose:
        print strResult + ' for x of ' + str(x)
    return sum


def anps(x, start, range, n):
    return alternating_newtonian_polynomial_sum(x, start, range, n, range - 1)


def canps(x, range, n, verbose=True):
    sum = 0
    i = 0
    start = -int(range/2) - 1 - ((range % 2) - 1)/2.00
    sign = 1
    strResult = 'canps\t'
    while i < range:
        temp = sum
        sum += (x + start + range - i)**n * sign * newton(range-1, i)
        if sign > 0:
            strResult += '+'
        else:
            strResult += '-'
        strResult += str(newton(range-1, i)) + 'x(|' + str(x+start+range-i) + '|)^' + str(n) + ' '
        i += 1
        sign *= -1
    if verbose:
        print strResult + ' for x of ' + str(x)
    return sum


def ranps(x, start, range, n, nt):
    return alternating_newtonian_polynomial_sum(x, start, range, n, nt)


def cranps(x, range, n, nt):
    return ranps(x, int(-range / 2) + 1, range, n, nt)


def poly_anes(x, start, range, n, verbose=True):
    sum = 0
    i = 0
    strResult = 'poly_anes\t'
    while i <= n:
        temp = sum
        temp2 = anes(1, range, i, True)
        print temp2
        sum += newton(n, i) * ((x+start-1) ** (n-i)) * temp2
        strResult += '+' + str(temp2) + '*' + str(newton(n,i)) + 'x(|' + str(start-1) +'|)^' + str(n-i) + ' '
        i += 1
    if verbose:
        print strResult + 'for x of ' + str(x)
    return sum


def poly_canes(x, range, n, verbose=True):
    start = -int(range/2) - 1 - ((range % 2) - 1)/2.00
    sum = 0
    i = 0
    strResult = 'poly_canes\t'
    while i <= n:
        temp = sum
        temp2 = anes(start+1, -start-1, i, False)
        sum += newton(n, i) * (x ** (n - i)) * temp2
        strResult += '+' + str(temp2) + '*' + str(newton(n, i)) + 'x' + str(n - i) + ' '
        i += 1
    if verbose:
        print strResult + 'for x of ' + str(x)
    return sum


x = 1
range = 3
n = 2
print poly_anes(x, 1, range, n)
print anps(x, 1, range, n)
print canps(x, range, n)
print(poly_canes(x, range, n))