const lockForm = (form) => {
    form.find(':input, button').attr('disabled', true);
};

const unlockForm = (form) => {
    form.find(':input, button').attr('disabled', false);
};

const clearForm = (form) => {
    form.find('input').val('');
};

const updateTextArea = (textArea, newValue) => {
    textArea.val(newValue);
    textArea.attr('rows', textArea.val().split("\n").length);
}

const prettyResult = (resultObj) => {
    return '(' + (new Date).toString() + ')\n--------------\n' + JSON.stringify(resultObj, null, 2);
};
