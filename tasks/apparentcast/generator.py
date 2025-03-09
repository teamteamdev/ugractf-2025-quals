import os
import random
import scapy.packet, scapy.layers.l2, scapy.layers.inet, scapy.utils

from kyzylborda_lib.generator import get_attachments_dir
from kyzylborda_lib.secrets import get_flag

def generate_stream(proto, src_ip, dst_ip, sport, dport, count=1000):
    stream = []
    base_seq = random.randint(1000000, 9999999)
    payload_sizes = {
        'http': (100, 1400),    # HTTP can have varying sizes
        'https': (50, 1200),    # HTTPS typically smaller due to encryption
        'ssh': (32, 256),       # SSH usually has smaller packets
        'smtp': (200, 800),     # SMTP emails
        'mysql': (64, 512)      # Database queries
    }
    
    # Initial handshake
    stream.append(
        scapy.layers.l2.Ether(src="4a:7a:8f:55:18:d3", dst="41:a7:b3:ee:00:01") /
        scapy.layers.inet.IP(src=src_ip, dst=dst_ip) /
        scapy.layers.inet.TCP(sport=sport, dport=dport, seq=base_seq, flags='S')
    )
    
    # Data packets
    for i in range(count):
        size = random.randint(*payload_sizes.get(proto, (64, 512)))
        stream.append(
            scapy.layers.l2.Ether(src="4a:7a:8f:55:18:d3", dst="41:a7:b3:ee:00:01") /
            scapy.layers.inet.IP(src=src_ip, dst=dst_ip) /
            scapy.layers.inet.TCP(sport=sport, dport=dport, seq=base_seq + i * 512, flags='PA') /
            scapy.packet.Raw(load=random.randbytes(size))
        )
    return stream

def generate():
    flag = get_flag()

    random.seed(int(flag.replace("_", ""), 36))

    letters = f"{random.randint(1000, 9999)}#{flag}#{random.randint(00000, 99999)}"
    transmission = b"".join(open(os.path.join("private", "letters", f"{c}.ts"), "rb").read() for c in letters)
    transmission = transmission[random.randint(99, 1048):] + random.randbytes(random.randint(3000, 4000))
    transmission = transmission[len(transmission) % 1481:]

    # Store all background streams separately
    background_streams = {
        'https': generate_stream(
            'https',
            "192.168.88.48", "151.101.1.140",
            random.randint(32768, 60999), 443
        ),
        'https2': generate_stream(
            'https',
            "192.168.88.48", "77.88.8.8",
            random.randint(32768, 60999), 443
        ),
        'ssh': generate_stream(
            'ssh',
            "192.168.88.48", "192.168.88.37",
            random.randint(32768, 60999), 22
        ),
    }

    # Generate DNS queries as a separate stream
    dns_stream = []
    for _ in range(1000):
        dns_payload = random.randbytes(random.randint(30, 60))
        dns_stream.append(
            scapy.layers.l2.Ether(src="4a:7a:8f:55:18:d3", dst="41:a7:b3:ee:00:01") /
            scapy.layers.inet.IP(src="192.168.88.48", dst="8.8.8.8") /
            scapy.layers.inet.UDP(sport=random.randint(32768, 60999), dport=53) /
            scapy.packet.Raw(load=dns_payload)
        )
    background_streams['dns'] = dns_stream

    # Initialize stream positions
    stream_positions = {k: 0 for k in background_streams}

    def inject_random_burst():
        # Select a random stream
        stream_name = random.choice(list(background_streams.keys()))
        stream = background_streams[stream_name]
        pos = stream_positions[stream_name]
        
        # Generate a burst of 1-20 packets
        burst_size = random.randint(1, 20)
        burst_packets = []
        
        for _ in range(burst_size):
            if pos >= len(stream):
                pos = 0  # Wrap around if we reach the end
            burst_packets.append(stream[pos])
            pos += 1
        
        stream_positions[stream_name] = pos
        return burst_packets

    packets = []
    t_pos = 0
    while t_pos < len(transmission):
        p_len = 1481
        cur_packets = []
        p = (
            scapy.layers.l2.Ether(src="4a:7a:8f:55:18:d3", dst="41:a7:b3:ee:00:01") /
            scapy.layers.inet.IP(src="239.1.6.66", dst="192.168.88.48") /
            scapy.layers.inet.UDP(sport=59007, dport=21935) /
            scapy.packet.Raw(load=transmission[t_pos:t_pos + p_len])
        )
        cur_packets.append(p)

        if random.random() < 0.1 or len(packets) < 200:
            cur_packets.extend(inject_random_burst())
        
        t_pos += p_len
        for p in cur_packets:
            p.time = 1741391399 + t_pos / (22188 / 2.40)
        packets.extend(cur_packets)

    scapy.utils.wrpcap(os.path.join(get_attachments_dir(), "apparentcast.pcap"), packets)