

def getMAC(rPi):
    ## Return the MAC address of the specified interface
    if rPi:
        strmac = open('/sys/class/net/wlan0/address').read()
    else:
        strmac = '00:ff:00:ff:00:ff'
    return int(strmac[0:17].replace(':',''),16)
