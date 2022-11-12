# this program retrieve wifi passwords from a windows computer
import subprocess
import os
import re
from collections import namedtuple
import configparser

def get_windows_saved_ssids(): # collect a list of saved ssids
    output = subprocess.check_output("netsh wlan show profiles").decode()
    ssids = []
    profiles = re.findall(r"All User Profile\s(.*)",output)
    for profile in profiles:
        ssid = profile.strip().strip(":").strip() #this removes spaces and colons from ssids
        ssids.append(ssid) # add the above stripped information to the list of ssids
    return ssids

def get_windows_saved_wifi_passwords(verbose=1):
    """Extract saved wifi passwords from windows machine
    Args:
        verbose (int,optional): printing saved profiles in real time. Defaults to 1.
    Returns:
        [list]: list of the extracted profiels which has the fields ["ssid", "cipher", "key"]
    """
    ssids = get_windows_saved_ssids()
    Profile = namedtuple("Profile", ["ssid", "ciphers", "key"])
    profiles = []
    for ssid in ssids:
        ssid_details = subprocess.check_output(f"""netsh wlan show profile "{ssid}" key=clear""").decode()
        # the above line gets the ciphers
        ciphers = re.findall(r"Cipher\s(.*)", ssid_details) # remove spaces and colon
        ciphers = "/".join([c.strip().strip(":").strip() for c in ciphers]) # this gets the actual
        key = re.findall(r"Key Content\s(.*)", ssid_details)
        
        try:
            key = key[0].strip().strip(":").strip()
        except IndexError:
            key = "None"
        profile = Profile(ssid=ssid, ciphers=ciphers, key=key)
        if verbose >= 1:
            print_windows_profile(profile)
        profiles.append(profile)
    return profiles

def print_windows_profile(profile): # prints a single profile on a window system
    print(f"{profile.ssid:25}{profile.ciphers:15}{profile.key:50}")
    
def print_windows_profiles(verbose): # print all f the ssids with keys on windows
    print("SSID                     CIPHER(S)                KEY")
    get_windows_saved_wifi_passwords(verbose)
    
def get_linux_saved_wifi_passwords(verbose=1):
        """Extracts wifi passwords from a linux system. This accesses data in '/etc/NetworkManager/system-connections/' directory
        Args:
            verbose(int,optional): option to print saved profiles in real-time. Defaults to 1.
        Returns:
            [list]: list of extracted profiles, a profile has the fields ["ssid", "auth-alg", "key-mgmt", "psk"]
        """
        network_connections_path = "/etc/NetworkManager/system-connections/"
        fields = ["ssid", "auth-alg", "key-mgmt", "psk"]
        Profile = namedtuple("Profile", [f.replace("-", "_") for f in fields])
        profiles = []
        for file in os.listdir(network_connections_path):
            date = {k.replace("-", "_"): None for k in fields}
            config = configparser.ConfigParser()
            config.read(os.path.join(network_connections_path, file))
            for _, section in config.items():
                for k, v in section.items():
                    if k in fields:
                        data[k.replace("-", "_")] = V
            profile = Profile(**data)
            if verbose >= 1:
                print_linux_profiles(profile)
            profiles.append(profile)
        return profiles
def print_linux_profiles(profile): # prints a single linux profile
    print(f"{str(profile.ssid):25}{str(rofile.auth_alg):5}{str(rofile.key_mgmt):10}{str(profile.psk):50}")
    
def print_linux_profiles(verbose=1): # prints all SSIDS and keys n psk
    print("SSID                    AUTH KEY-MGMT              PSK")
    get_linux_saved_wifi_passwords(verbose)

def print_profiles(verbose=1):
    if os.name == "nt":
        print_windows_profiles(verbose)
    elif os.name == "posix":
        print_linux_profiles(verbose)
    else:
        raise NotImplemented("This program only works on linux and windows")
        
if __name__=="__main__":
    print_profiles()
