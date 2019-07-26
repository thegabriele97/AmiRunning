
function openInNewTab(url) {
    var win = window.open(url, '_blank');
    win.focus();
}

function getJSONUserTurnUrl(pos) {
    return 'http://' + location.host + '/user/' + pos + '/is_turn';
}

function getJSONSystemTempUrl() {
    return 'http://' + location.host + '/system/data/temp';
}

function getJSONSystemLuminiscenceUrl() {
    return 'http://' + location.host + '/system/data/luminiscence';
}

function getJSONSystemHumidity() {
    return 'http://' + location.host + '/system/data/humidity';
}

function postRequest(path, parameters) {
    var form = $('<form></form>');

    form.attr("method", "post");
    form.attr("action", path);

    $.each(parameters, function(key, value) {
        var field = $('<input></input>');

        field.attr("type", "hidden");
        field.attr("name", key);
        field.attr("value", value);

        form.append(field);
    });

    // The form needs to be a part of the document in
    // order for us to be able to submit it.
    $(document.body).append(form);
    form.submit();
}