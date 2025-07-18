#conver processing code to function
def process_result(data):
    nested_values = ['author', 'authorStats', 'authorStatsV2', 'music','video','stats', 'statsV2',
                'challenges', 'backendSourceEventTracking', 'contents','item_control', 'textExtra', 'videoSuggestWordsList']
    skip_values = ['challenges', 'backendSourceEventTracking', 'contents','item_control', 'textExtra', 'videoSuggestWordsList']

    #create blanck dictionary
    flattened_data = {}
    #Loop through each video
    for idx, value in enumerate(data):
        flattened_data[idx] = {}
        #Loop through each property in each video
        for prop_idx, prop_value in value.items():
            #check if nested
            if prop_idx in nested_values:
                if prop_idx in skip_values:
                    pass
                else:
                    #loop through each nested property
                    for nested_idx, nested_value in prop_value.items():
                        flattened_data[idx][prop_idx+'_'+nested_idx] = nested_value
            #if its not nested, add it back to the dictionary
            else:
                flattened_data[idx][prop_idx] = prop_value

    return flattened_data