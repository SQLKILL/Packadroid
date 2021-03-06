import os
import shutil
import subprocess as sp

from packadroid.manifestmanager import manifest_analyzer, manifest_changer

def decompile_apk(apkPath, verbose):
    """
    Decompile the .apk file given as parameter.

    :param apkPath: Path to the original apk file.
    :param verbose: specify whether to output enriched terminal output.
    :type apkPath: str

    :return The path to the directory containing the decompiled application.
            If an error occurs, we will return None
    """
    if not os.path.isfile(apkPath):
        return None
    outDir = os.path.splitext(apkPath)[0] +  "_decompiled"
    # try removing output directory if it is already present
    try:
        shutil.rmtree(outDir)
    except:
        #good to go
        pass
    decompiler = sp.Popen("apktool d  -o {} {}".format(outDir, apkPath).split(" "), stdout=sp.PIPE, stderr=sp.PIPE)#stdout=sp.PIPE)
    out,err = decompiler.communicate()
    if verbose:
        print(out.decode('ascii'))
        print(err.decode('ascii'))

    if decompiler.returncode != 0:
        print("[-] Error during decompilation. Return code of apktool: {}".format(decompiler.returncode))
        shutil.rmtree(outDir)
        return None
    if "Error" in out.decode('ascii'):
        print("[-] Error during decompilation.")
        shutil.rmtree(outDir)
        return None
    return outDir

def __run_jarsigner(command):
    """ executes the jarsigner with specific options given in the 'command' argument

    :param command: Parameters for jarsigner.
    :type command: str
    """

    print("[*] Sign the repacked application")
    full_command = "jarsigner " + command
    proc = sp.Popen(full_command, stdout=sp.PIPE, shell=True)
    (out, err) = proc.communicate()

def repack_apk(decompiled_path, hooks, output, verbose):
    """
    Build/Repack the decompiled application given as parameter.

    :param decompiled_path: The path to the directory to the decompiled application.
    :type decompiled_path: str

    :param hooks: The hooks we inserted beforehand. Those contain the paths to the smali files we need to copy.
    :type hooks: :type hooks: [:class:'hookmanager.Hook']

    :param output: The path where we should write the output to.
    :type output: str

    :param verbose: Specify whether to enable enriched terminal output.
    :type verbose: bool

    :return The path to the repacked .apk file.
            None is returned on any errors.
    """
    if not os.path.isdir(decompiled_path):
        return None

    __inject_payload(decompiled_path, hooks)
    __add_necessary_permissions(decompiled_path, hooks)

    decompiler = sp.Popen("apktool b -o {} {}".format(output, decompiled_path).split(" "), stdout=sp.PIPE, stderr=sp.PIPE)
    out,err = decompiler.communicate()
    if verbose:
        print(out.decode('ascii'))
        print(err.decode('ascii'))

    __run_jarsigner(
        "-verbose -keystore ~/.android/debug.keystore -storepass android -keypass android -digestalg SHA1 -sigalg "
        "MD5withRSA " + output + " androiddebugkey")

def __inject_payload(original_apk_dec_path, hooks):
    """
        Copy the smali sources of the payload to the original application before building.

        :param original_apk_dec_path: Path to the decompiled original apk.
        :type original_apk_dec_path: str

        :param hooks: The hooks we inserted beforehand. Those contain the paths to the smali files we need to copy.
        :type hooks: :type hooks: [:class:'hookmanager.Hook']
    """
    original = os.path.join(original_apk_dec_path, "smali")
    payload_paths = set([h.get_payload_dec_path() for h in hooks])
    for path in payload_paths:
        payload = os.path.join(path, "smali")
        for subf in os.listdir(payload):
            if subf != "android":
                os.system("cp -r {} {}".format(os.path.join(payload, subf), original))

def __add_necessary_permissions(original_apk_dec_path, hooks):
    """
    This functions adds additional permissions to the original application if they
    are required for the payload.

    :param original_apk_dec_path: Path to the decompiled original application.
    :type original_apk_dec_path: str

    :param hooks: The hooks we inserted into the original apk.
    :type hooks: [:class:'packadroid.hookmanager.hook.Hook']
    """
    original_apk_manifest_path = os.path.join(original_apk_dec_path, "AndroidManifest.xml")
    original_permissions = manifest_analyzer.get_permissions(original_apk_manifest_path)

    payload_permissions = []
    for hook in hooks:
        payload_permissions.extend(manifest_analyzer.get_permissions(os.path.join(hook.get_payload_dec_path(), "AndroidManifest.xml")))

    payload_permissions = set(payload_permissions)
    manifest_changer.add_permissions_to_manifest(original_apk_manifest_path, payload_permissions.difference(original_permissions))
