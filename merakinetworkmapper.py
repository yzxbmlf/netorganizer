from merakifixedipreservationsgenerator import MerakiFixedIpReservationsGenerator
from merakiwrapper import MerakiWrapper
from ipv4privatenetworkspace import Ipv4PrivateNetworkSpace

class MerakiNetworkMapper() :

    def __init__(self, device_table, meraki_wrapper) -> None:
        self.meraki_wrapper = meraki_wrapper
        self.device_table = device_table
        self.network_space = Ipv4PrivateNetworkSpace(meraki_wrapper.vlan_subnet)
    
    def find_ips(self) -> list:
        df = self.device_table.df
        #l = [ip for ip in df.ip.unique.tolist() if ip]
        l = df.query("ip != ''")['ip'].tolist() 
        return l

    def find_macs_needing_ip(self) -> list:
        df = self.device_table.df
        l = df.query("ip == ''")['mac'].tolist() 
        return l

    def assign_ip(self,mac) : 
        df = self.device_table.df
        df.loc[df["mac"] == mac, "ip"] = self.network_space.allocate_address()

    def map_devices_to_network_space(self) :
        if self.device_table.has_unique_ips() : 
            # Persist exising reservations
            ips = self.find_ips() 
            for ip in ips : 
                self.network_space.allocate_specific_address(ip)
            macs_needing_ip = self.find_macs_needing_ip()
            # Newly registered devices will need an IP address
            for mac in macs_needing_ip : 
                self.assign_ip(mac)
            # Now generate new set of fixedIP reservations - MerakiFixedIpReservationsGenerator
            fixed_ip_reservations_generator = MerakiFixedIpReservationsGenerator()
            fixed_ip_reservations = fixed_ip_reservations_generator.generate(self.device_table)
            print(fixed_ip_reservations)
            # Now tell Meraki

            