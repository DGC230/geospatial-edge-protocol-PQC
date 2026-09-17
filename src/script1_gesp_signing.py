import struct
import hashlib
import time
from dataclasses import dataclass
from collections import defaultdict

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

FRESHNESS_WINDOW_S = 30
_PACKET_FMT = ">HiifIB"


@dataclass
class SpatialPacket:
    node_id: int
    latitude: float
    longitude: float
    sensor_val: float
    timestamp: int
    seq_num: int

    def to_bytes(self) -> bytes:
        return struct.pack(
            _PACKET_FMT,
            self.node_id & 0xFFFF,
            int(round(self.latitude * 1e7)),
            int(round(self.longitude * 1e7)),
            float(self.sensor_val),
            self.timestamp & 0xFFFFFFFF,
            self.seq_num & 0xFF,
        )


@dataclass
class SignedFrame:
    packet: SpatialPacket
    signature: bytes
    pub_key_der: bytes


class SensorNode:
    def __init__(self, node_id: int):
        self.node_id = node_id
        self._seq = 0
        self._sk = ec.generate_private_key(ec.SECP256R1())
        self.pk = self._sk.public_key()
        self.pk_der = self.pk.public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def _sign(self, pkt: SpatialPacket) -> bytes:
        digest = hashlib.sha256(pkt.to_bytes()).digest()
        return self._sk.sign(digest, ec.ECDSA(Prehashed(hashes.SHA256())))

    def build_and_sign(self, lat, lon, sensor_val, timestamp=None) -> SignedFrame:
        self._seq = (self._seq + 1) % 256
        ts = int(time.time()) if timestamp is None else int(timestamp)
        pkt = SpatialPacket(
            node_id=self.node_id, latitude=lat,
            longitude=lon, sensor_val=sensor_val,
            timestamp=ts, seq_num=self._seq)
        return SignedFrame(packet=pkt, signature=self._sign(pkt),
                           pub_key_der=self.pk_der)


class EdgeGateway:
    def __init__(self, freshness_window: int = FRESHNESS_WINDOW_S):
        self.freshness_window = freshness_window
        self._cert_store = {}
        self._seq_table = defaultdict(int)

    def register(self, node_id: int, pub_key_der: bytes) -> None:
        self._cert_store[node_id] = serialization.load_der_public_key(pub_key_der)

    def verify(self, frame: SignedFrame):
        pkt = frame.packet
        pk = self._cert_store.get(pkt.node_id)
        if pk is None:
            return False, "UNKNOWN_NODE"
        digest = hashlib.sha256(pkt.to_bytes()).digest()
        try:
            pk.verify(frame.signature, digest, ec.ECDSA(Prehashed(hashes.SHA256())))
        except InvalidSignature:
            return False, "INVALID_SIGNATURE"
        if abs(int(time.time()) - pkt.timestamp) > self.freshness_window:
            return False, "STALE_PACKET"
        if pkt.seq_num <= self._seq_table[pkt.node_id]:
            return False, "REPLAY"
        self._seq_table[pkt.node_id] = pkt.seq_num
        return True, "ACCEPTED"


def _demo():
    node = SensorNode(node_id=42)
    gw = EdgeGateway()
    gw.register(node.node_id, node.pk_der)

    frame = node.build_and_sign(lat=41.0082, lon=28.9784, sensor_val=17.3)
    print("valid frame        ->", gw.verify(frame))

    tampered = SignedFrame(frame.packet, b"\x00" + frame.signature[1:], frame.pub_key_der)
    print("tampered signature ->", gw.verify(tampered))

    print("replayed frame     ->", gw.verify(frame))

    stale = node.build_and_sign(lat=41.0082, lon=28.9784, sensor_val=17.4,
                                timestamp=int(time.time()) - (FRESHNESS_WINDOW_S + 5))
    print("stale frame        ->", gw.verify(stale))


if __name__ == "__main__":
    _demo()
