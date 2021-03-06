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

        result.append( (get_activity_name(activity), is_launcher_activity) )
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