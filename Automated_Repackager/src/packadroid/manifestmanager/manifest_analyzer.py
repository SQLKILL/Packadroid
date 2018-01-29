import xml.etree.ElementTree as ET


def get_activity_name(activity):
    """returns name of xml encoded activity. (name may be dirty with android tags)"""
    for key in activity.attrib.keys():
        if key.endswith("name"):
            return activity.attrib[key]


def find_all_activities(manifest_path):
    """
        Finds all activities specified in a certain 
        manifest. It also examines whether the activity
        is a launcher activity and extracts this 
        information as a bool flag.

        :param manifest_path: path to a file containing a manifest
        :return: returns a list of 2-tuples, where each entry 
        contains (activity_name, is_launcher_activity).
    """
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    package = root.attrib['package']

    application = [child for child in root if child.tag == 'application']
    activities = [x for x in application[0] if x.tag == 'activity']

    result = []

    for activity in activities:
        is_launcher_activity = False

        intent_filters = [x for x in activity if x.tag == 'intent-filter']
        for intent_filter in intent_filters:
            if intent_filter.attrib != {}:
                for category in intent_filter:
                    if category.tag == 'category':
                        if ('{http://schemas.android.com/apk/res/android}name' in category.attrib
                            and category.attrib['{http://schemas.android.com/apk/res/android}name'] == "android.intent.category.LAUNCHER"):
                            is_launcher_activity = True

        result.append( (activity, is_launcher_activity) )
    return result



def find_launcher_activities(manifest_path):
    """
        Finds the launcher activity (or multiple) from xml.etree.ElementTree.
        Given: Manifest Path
    """
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    package = root.attrib['package']

    application = [child for child in root if child.tag == 'application']
    activities = [x for x in application[0] if x.tag == 'activity']

    activities_with_intent_filter = []

    for activity in activities:
        # print activity
        intent_filters = [x for x in activity if x.tag == 'intent-filter']
        for intent_filter in intent_filters:
            #for action in [x for x in intent_filter if x.tag == 'action']:
                #if ('{http://schemas.android.com/apk/res/android}name' in action.attrib
                    #and action.attrib['{http://schemas.android.com/apk/res/android}name'] == "android.intent.action.MAIN"):
                    #activities_with_intent_filter.append(get_activity_name(activity))

            if intent_filter.attrib != {}:
                for category in intent_filter:
                    if category.tag == 'category':
                        if ('{http://schemas.android.com/apk/res/android}name' in category.attrib
                            and category.attrib['{http://schemas.android.com/apk/res/android}name'] == "android.intent.category.LAUNCHER"):
                            activities_with_intent_filter.append(get_activity_name(activity))
    return list(set(activities_with_intent_filter))


def get_permissions(manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()

    permissions = [x for x in root if "permission" in x.tag]

    permissions = [x.attrib["{http://schemas.android.com/apk/res/android}name"] for x in permissions]

    return list(set(permissions))

<<<<<<< HEAD:Automated_Repackager/pythonFiles/apkhandling/manifest_analyzer.py

def fix_manifest(payload_manifest_path, original_manifest_path,
                 output_manifest_path):
    """
        Fix manifest located at the provided manifest path.
        :param manifest_path:
        :return:
    """
    payload_permissions = get_permissions(payload_manifest_path)

    original_permissions = get_permissions(original_manifest_path)

    add_permissions = [x for x in payload_permissions if x not in original_permissions]

    manifest_lines = []
    with open(original_manifest_path) as f:
        manifest_lines.extend(f.readlines())

    inject = 0
    novel_manifest = []
    for line in manifest_lines:
        if "uses-permission" in line and inject == 0:
            for permission in add_permissions:
                print permission
                novel_manifest.append("<uses-permission android:name=\"" + permission + "\" />")
            novel_manifest.append(line)
            inject = 1
        else:
            novel_manifest.append(line)

    with open(output_manifest_path, "w") as f:
        for line in novel_manifest:
            f.write(line + "\n")


if __name__ == "__main__":
    x = find_launcher_activity('../AndroidManifest.xml')
    print(x)
=======
>>>>>>> fa39a678ec10e2e6fc068b638703e4c483428776:Automated_Repackager/src/packadroid/manifestmanager/manifest_analyzer.py