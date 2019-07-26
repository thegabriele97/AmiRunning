function activateElementRefreshJSON(JSONResponseURL, elementIdToRefesh, JSONfield, timeout=10000){

    let f = function() {
        
        let request = new XMLHttpRequest();
        request.onreadystatechange = () => {
            if (request.readyState == 4 && request.status == 200) {
                let data = JSON.parse(request.responseText);
                document.getElementById(elementIdToRefesh).innerText = data[JSONfield];
            }
        };

        request.open('GET', JSONResponseURL, true);
        request.send();

    };

    f();
    setInterval(f, timeout);
}