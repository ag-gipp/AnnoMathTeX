
function handleNoMatch(){
    /*
    The "No Match" button was clicked: The user did not find any of the recommendations to be fitting.
    This means that this information has to be added to the "annotations" dictionary, which will later be written to the
    evaluation csv file, along with the other annotations.

    This method is also called if the user deselects the "No Match" button, i.e. if he found a matching recommendation
    after all.
     */

    var name = document.getElementById('noMatchInput').value;


    //setAnnotatedColor([uniqueID);
    //handleLinkedTokens(addToAnnotated);
    var uIDs = getLinkedIDs(tokenContent);
    addToAnnotations(uniqueID, name, 'user', '-', true, uIDs);
    setAnnotatedColor(uIDs);
    populateTable();
    renderAnnotationsTable();
}



function addToAnnotations(uID, name, source, rowNum, noMatch=false, uIDs = null) {



    function localDict() {
        return {
                'name': name,
                'mathEnv': mathEnv,
                'source': source,
                'rowNum': rowNum,
                'sourcesWithNums': noMatch ? {} : sourcesWithNums[name]
            };
    }

    var local = document.getElementById('localSwitch').checked;
    if (local) {
        if (tokenContent in annotations['local']){
            annotations['local'][tokenContent][uID] = localDict();
        } else {
            annotations['local'][tokenContent] = {};
            annotations['local'][tokenContent][uID] = localDict();
        }
    } else {

        console.log(tokenContent);

        annotations['global'][tokenContent] = {
        'name': name,
        'uniqueIDs': uIDs,
        'sourcesWithNums': noMatch ? {} : sourcesWithNums[name]
        };
    }
}




function deleteLocalAnnotation(token, uID) {
    delete annotations['local'][token][uID];
}

function deleteGlobalAnnotation(token) {
    delete annotations['global'][token];
}

function deleteFromAnnotations(argsString) {
    var argsArray = argsString.split('----');

    var token = argsArray[0];
    var local = (argsArray[1] == 'true');
    var uIDs = argsArray[2].split(',');
    if (local) {
        deleteLocalAnnotation(token, uIDs[0]);
        setBasicColor(uIDs);
    } else {
        deleteGlobalAnnotation(token);
        setBasicColor(uIDs);
    }
    renderAnnotationsTable();
}




function handleExistingAnnotations(existing_annotations){
    /*
    If any previous annotations for the same document exist, a number of actions are made:
        - The annotations are added to the dictionary "annotations".
        - The table at the top of the document containing the current annotations is filled with the existing ones.
        - The tokens that were annotated are colored accordingly.
     */
    annotations = JSON.parse(existing_annotations)['existingAnnotations'];
    uIDs = getLocalUniqueIDs().concat(getGlobalUniqueIDs());
    setAnnotatedColor(uIDs);
    renderAnnotationsTable();
}

