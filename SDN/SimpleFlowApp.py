#!/usr/bin/env python3

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3

class SimpleFlowApp(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleFlowApp, self).__init__(*args, **kwargs)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, MAIN_DISPATCHER)
    def switch_features_handler(self, ev):
        """Es crida quan un switch OpenFlow es connecta al controlador."""
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Instal.lem una norma per a TCP
        match_tcp = parser.OFPMatch(ip_proto=6)  # 6 == TCP
        actions_tcp = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.add_flow(datapath, 1, match_tcp, actions_tcp)

        # Instal.lem una norma per a UDP
        match_udp = parser.OFPMatch(ip_proto=17) # 17 == UDP
        actions_udp = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.add_flow(datapath, 1, match_udp, actions_udp)

        # Per a altres tipus de paquets (ICMP, ARP, etc.)
        match_any = parser.OFPMatch()
        actions_any = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        self.add_flow(datapath, 0, match_any, actions_any)

    def add_flow(self, datapath, priority, match, actions):
        """Utilitat per enviar una norma de flux al switch."""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority,
            match=match, instructions=inst)
        datapath.send_msg(mod)
