import pyshark

filename = 'data/L_cyber_ff_09-17__11_37_53.pcap.TCP_10-0-0-9_59515_212-179-180-110_443.pcap'
received = list(pyshark.FileCapture(filename, display_filter='tcp.srcport == 443'))
sent = list(pyshark.FileCapture(filename, display_filter='tcp.dstport == 443'))
len(received)
p = sent[5]
p.captured_length
p.sniff_timestamp
p.ip.ttl
