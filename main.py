from mindwave import Mindwave

mindwave = Mindwave()
mindwave.connect('/dev/rfcomm0')

while True:
    data = mindwave.parse()
    if data:
        print(data)

mindwave.close()