a = ['5', '11']
for i in range(0, len(a) - 1):
    print i
    for j in range(0, len(a) - 1 - i):
        print "xxxx:", a[j], a[j+1]
        if a[j] < a[j + 1]:
            tmp = a[j]
            a[j] = a[j + 1]
            a[j + 1] = tmp
            print "swap:", a[j], a[j + 1]
        print(a)
print(a)
