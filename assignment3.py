import stdiomask
import subprocess
import polling


class ConnectWifi:
    def __init__(self, interface):
        """
        :param interface: name of the wifi interface on the machine
        """
        self.interface_name = interface
        
    def getAvailableNetworks(self):
        """
        This function find all the available wifi networks
        :return: dictionary of wifi network details in order of their strengths
        """

        command = ["netsh", "wlan", "show", "networks", "interface", "=", self.interface_name, "mode", "=", "bssid"]
        out = subprocess.check_output(command)
        devices = out.decode('ascii')
        devices = devices.replace("\r","")

        networks = []
        last_id = None
        tmp = {}
        
        for val in devices.split("\n"):
            if "BSSID" in val:
                continue
            elif "SSID" in val:
                if last_id is not None:
                    networks.append(tmp)
                
                last_id = val.split(":")[1].strip()
                tmp = {}
                tmp["ssid"] = last_id
            elif last_id is not None:
                if "Authentication" in val:
                    tmp["authentication"] = val.split(":")[1].strip()
                elif "Encryption" in val:
                    tmp["encryption"] = val.split(":")[1].strip()
                elif "Signal" in val:
                    tmp["signal"] = int(val.split(":")[1].strip()[0:-1])

        networks.append(tmp)
        
        networks = sorted(networks, key = lambda x: x["signal"], reverse = True)

        mapper = {}
        for i in range(0,len(networks)):
            mapper[i+1] = networks[i]

        return mapper

    def deleteProfile(self, name):
        """
        This function deletes the network profile file for the given profile name if it exists.
        :param name: profile name to delete
        :return: None
        """
        out = subprocess.check_output(["netsh", "wlan", "delete", "profile", name])
        
    def createConnection(self, name, ssid, password, authentication, encryption):
        """
        This function creates network profile based on the details given such as password, ssid.

        :param name: profile name
        :param ssid: network ssid
        :param password: wifi password
        :param authentication: authentication type
        :param encryption: encryption type
        :return: None
        """
        config = """<?xml version=\"1.0\"?>
                    <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
                    <name>"""+name+"""</name>
                    <SSIDConfig>
                            <SSID>
                                    <name>"""+ssid+"""</name>
                            </SSID>
                    </SSIDConfig>
                    <connectionType>ESS</connectionType>
                    <connectionMode>auto</connectionMode>
                    <MSM>
                            <security>
                                    <authEncryption>
                                            <authentication>WPA2PSK</authentication>
                                            <encryption>AES</encryption>
                                            <useOneX>false</useOneX>
                                    </authEncryption>
                                    <sharedKey>
                                            <keyType>passPhrase</keyType>
                                            <protected>false</protected>
                                            <keyMaterial>"""+password+"""</keyMaterial>
                                    </sharedKey>
                            </security>
                    </MSM>
                </WLANProfile>"""

        command = ["netsh", "wlan", "add", "profile", "filename", "=", f"\"{name}.xml\"", "interface", "=", self.interface_name]

        with open(name+".xml", "w") as file:
            file.write(config)

        try:
            out = subprocess.check_output(command)
        except Exception as e:
            raise Exception("Unable to save network profile")

    def connect(self, name, ssid):
        """
        This functions connects to the wifi having input profile name and ssid.

        This function connects to the given profile name considering network profile exists,
        i.e, created by createConnection function.

        :param name: profile name
        :param ssid: ssid of the wifi
        :return: None
        """
        command = ["netsh", "wlan", "connect", "name", "=", f"\"{name}\"", "ssid", "=", f"\"{ssid}\"", "interface", "=", self.interface_name]
        try:
            out = subprocess.check_output(command)
        except Exception as e:
            raise Exception("Unable to connect to this profile")

    def checkConnectionStatus(self, name, ssid):
        """
        This function checks if the the input profile name and ssid is connected as wifi network or not

        :param name: profile name of the wifi to be checked if currently connected or not
        :param ssid: ssid of the wifi to be checked if currently connected or not
        :return: boolean, True if the given profile name and ssid is currenlty connected
                          False if the given profile name and ssid is not connected.
        """
        command = ["netsh", "wlan", "show", "interface", "name", "=", self.interface_name]
        try:
            out = subprocess.check_output(command)
            details = out.decode('ascii')
            details = details.replace("\r","")

            connectionInfo = {}
            for val in details.split("\n"):
                if "State" in val:
                    connectionInfo["State"] = val.split(":")[1].strip()
                elif "Profile" in val:
                    connectionInfo["Profile"] = val.split(":")[1].strip()

            if connectionInfo.get("State", -1) == "connected" and connectionInfo.get("Profile", -1) == name:
                print("Connected!")
                return True

            return False
        except Exception as e:
            raise Exception("Unable to get connection status")


if __name__ == '__main__':
    
    wifiobject = ConnectWifi("Wi-Fi")                 # creating ConnectWifi class object with "Wi-Fi" interface name
    allnetworks = wifiobject.getAvailableNetworks()   # getting all the available networks

    print("Your available wifi networks are: ",end=" ")
    count=0
    for val in allnetworks:                                     # printing top 3 signal strength networks
        print("["+str(val)+"]", allnetworks[val]["ssid"])
        count = count+1
        if count == 3:
            break

    choice = int(input("Your Choice? "))                        # taking user input choice to connect to which wifi
    password = stdiomask.getpass("Password : ")                 # taking password input

    if choice > count or choice < 1:                            # checking if input choice is valid or not
        print("Invalid choice")
    elif not password:                                          # making sure password is entered by the user
        print("Please provide a password")
    else:
        name = allnetworks[choice]["ssid"]                      # fetching ssid of the wifi which user has chosen
        auth = allnetworks[choice]["authentication"]            # fetching authentication details of the chosen wifi
        encryp = allnetworks[choice]["encryption"]              # fetching encryption details of chosen wifi

        try:
            wifiobject.deleteProfile(name)                      # deleting pre existing wifi profile
            wifiobject.createConnection(name, name, password, auth, encryp)     # creating new wifi profile with
                                                                                # the chosen ssid and password
            wifiobject.connect(name, name)                      # connecting to the wifi
        except Exception as e:
            print("Not Connected!")
        else:                                   # polling the checkConnectionStatus fn for 8 secs to check
                                                # if the wifi has been connected or not.
            try:
                polling.poll(
                    lambda: wifiobject.checkConnectionStatus(name, name) == True,
                    step = 2,
                    timeout = 8)
            except polling.TimeoutException:
                print("Not Connected!")
