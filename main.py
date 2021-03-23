from mindwave import Mindwave, Parser

mindwave = Mindwave()
mindwave.connect('/dev/rfcomm0')
parser = Parser(mindwave)

while True:
    data = parser()
    if data:
        print(data)

mindwave.close()