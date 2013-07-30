import Listeners


class Dechunker:

    def __init__(self):
        self.data = ''
        self.waiting_for_chunk = True
        self.bytes_to_eat = 0

    def feed(self, packet):
        if self.waiting_for_chunk:
            chunk_len, packet = packet.split("\r\n", 1)
            self.bytes_to_eat = int(chunk_len, 16)
            self.waiting_for_chunk = False

            if self.bytes_to_eat == 0:
                raise Listeners.SocketClosed()

        amount_edible = min(len(packet), self.bytes_to_eat)
        meal = packet[:amount_edible]

        self.data += meal
        self.bytes_to_eat -= amount_edible

        if self.bytes_to_eat == 0:
            self.waiting_for_chunk = True

            if amount_edible + 1 < len(packet):
                if not packet[amount_edible + 1:].strip() == '':
                    self.feed(packet[amount_edible + 1:].lstrip())

    def dump(self):
        return self.data


if __name__ == '__main__':
    packet_names = ["facebookcss/%i" % i for i in range(0, 34)]
    packets = []
    for packet_name in packet_names:
        with open(packet_name, "rb") as packet:
            packets.append(packet.read())

    dechunker = Dechunker()

    for i in range(37):
        if i > 33:
            exit("Fed illegal packet")
        try:
            print "Feeding packet %i" % i
            dechunker.feed(packets[i])
        except Listeners.SocketClosed:
            with open("facebookcss/complete.css", "wb") as css:
                css.write(dechunker.dump())
            exit("Success")
