import qrcode
def make_qr(data):
    img = qrcode.make(data)
    return img