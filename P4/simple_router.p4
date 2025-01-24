/* ----------------------------------------------------------------------------
 * simple_router.p4
 *
 * Exemple senzill d'un router fet en P4 per a l'arquitectura v1model de BMv2.
 * ----------------------------------------------------------------------------*/

#include <core.p4>
#include <v1model.p4>

/* headers */
header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

/* Estructura per emmagatzemar els headers */
struct headers {
    ethernet_t ethernet;
    ipv4_t     ipv4;
}

/* Metadades de P4 (exemple senzill, sense res addicional) */
struct metadata {
    /* Res en aquest exemple */
}

/* Pipeline v1model */
parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        /* Primer parsegem Ethernet */
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            0x0800: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }
}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {
        /* En aquest exemple no es realitza res */
    }
}

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action send_to_cpu() {
        standard_metadata.egress_spec = 0; // Envia a la CPU per manejar ARP
    }
    action ipv4_forward(bit<48> dstMac, bit<9> port) {
        hdr.ethernet.dstAddr = dstMac;
        standard_metadata.egress_spec = port;
    }

    action drop() {
        /* No fem res, el paquet es descarta */
        standard_metadata.egress_spec = 0;
    }
    
    /* Definim una taula senzilla per determinar la sortida (egress port)
       i la nova MAC de dst depenent de la IP. */
       
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward; // Declare the parameters explicitly
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop;
    }

    apply {
        if (hdr.ethernet.etherType == 0x0806) { // ARP packets
            send_to_cpu();
            return;
        }
        if (hdr.ethernet.etherType == 0x0800) { /* IPv4 */
            ipv4_lpm.apply();
        }
    }
}

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {
        /* En aquest exemple no es fa processament a l'egress */
    }
}

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply {
        /* No es calcula la checksum en aquest exemple  */
    }
}

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
    }
}

/* Instanciem la pipeline per a l'arquitectura v1model */
V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
