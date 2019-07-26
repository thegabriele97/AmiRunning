_user_pos = 0
_post_data = 0x1

function activateReloadOnUserTurn(JSONResponseURL, elementIdToRefesh, timeout=2000){

    setInterval(function() {
        
        let request = new XMLHttpRequest(); 
        request.onreadystatechange = () => {
            if (request.readyState == 4 && request.status == 200) {
                let data = JSON.parse(request.responseText);
                let is_user_turn = data['is_user_turn'];
                if (is_user_turn) {
                    location.reload();
                } else {
                   document.getElementById(elementIdToRefesh).innerText = data['remaining_user'];
                }
            }
        };

        request.open('GET', JSONResponseURL, true);
        request.send();

    }, timeout);
}

function getEventClosePage() {
    let isOnIOS = navigator.userAgent.match(/iPad/i)|| navigator.userAgent.match(/iPhone/i);
    return isOnIOS ? "pagehide" : "beforeunload";
}

function activateAutoLeaveQueueonExit(user_pos, post_data = '0x1') {
    _user_pos = user_pos;
    _post_data = post_data;
    window.addEventListener(getEventClosePage(), sendBeaconEvent);
}

function sendBeaconEvent() {
    console.log('Sending beacon..');
    navigator.sendBeacon('/user/' + _user_pos + '/leave_queue', _post_data);
}

function removeAutoReload() {
    window.removeEventListener(getEventClosePage(), sendBeaconEvent);
}