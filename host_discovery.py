from host_db import HostDB
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, arp


class HostDiscovery(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(HostDiscovery, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.host_db = HostDB()

        #  IMPORTANT: map (switch, port) → MAC
        self.port_to_mac = {}

    # ---------------- PRINT ----------------
    def print_hosts(self):
        hosts = self.host_db.get_hosts()

        print("\nUPDATED HOST TABLE:")
        print("-------------------------------------------------------------")
        print("{:<20} {:<15} {:<10} {:<10}".format(
            "MAC Address", "IP Address", "Switch", "Port"))
        print("-------------------------------------------------------------")

        for mac, details in hosts.items():
            print("{:<20} {:<15} {:<10} {:<10}".format(
                mac,
                details["ip"],
                details["switch"],
                details["port"]
            ))

        print("-------------------------------------------------------------")

    # ---------------- SWITCH INIT ----------------
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        self.host_db.hosts.clear()
        self.port_to_mac.clear()

        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=0,
            match=match,
            instructions=inst
        )

        datapath.send_msg(mod)

    # ---------------- PORT DOWN HANDLER (REAL FIX) ----------------
    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def port_status_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        port_no = msg.desc.port_no
        ofproto = datapath.ofproto

        if msg.desc.state & ofproto.OFPPS_LINK_DOWN:
            print(f"\nPort DOWN detected -> Switch {dpid}, Port {port_no}")

            key = (dpid, port_no)

            if key in self.port_to_mac:
                mac = self.port_to_mac[key]

                hosts = self.host_db.get_hosts()
                if mac in hosts:
                    del hosts[mac]
                    print(f"Host removed: {mac}")

                del self.port_to_mac[key]

                self.print_hosts()
            else:
                print("No host mapped to this port")

    # ---------------- PACKET IN ----------------
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == 35020:
            return

        src = eth.src
        dst = eth.dst
        dpid = datapath.id

        arp_pkt = pkt.get_protocol(arp.arp)

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        hosts = self.host_db.get_hosts()
        new_host = False

        # -------- ADD HOST --------
        if arp_pkt:
            ip_addr = arp_pkt.src_ip

            if src not in hosts:
                self.host_db.add_host(src, dpid, in_port, ip_addr)
                new_host = True

                print("\nNew Host Detected")
                print("MAC    :", src)
                print("IP     :", ip_addr)
                print("Switch :", dpid)
                print("Port   :", in_port)

            else:
                hosts[src]["ip"] = ip_addr
                hosts[src]["switch"] = dpid
                hosts[src]["port"] = in_port

            #  update port mapping
            self.port_to_mac[(dpid, in_port)] = src

        if new_host:
            self.print_hosts()

        # -------- FORWARDING --------
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)

            inst = [parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS, actions)]

            mod = parser.OFPFlowMod(
                datapath=datapath,
                priority=1,
                match=match,
                instructions=inst
            )

            datapath.send_msg(mod)

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )

        datapath.send_msg(out)
