function insert_message() {
    var sourceElement = document.getElementById('copy');
    var destinationElement = document.getElementById('paste');
    var copiedText = sourceElement.innerText;
    destinationElement.value = copiedText;      
}

// Function to compare the values of the two fields
function compareFields() {
    var value1 = field1.value;
    var value2 = field2.value;

    // Check if the values match
    if (value1 === value2) {

        resultParagraph.innerText = 'Match';
    } else {
        resultParagraph.innerText = 'Entries do not match.';
    }
}

// Get references to the input fields and result paragraph
var field1 = document.getElementById('pw1');
var field2 = document.getElementById('pw2');
var resultParagraph = document.getElementById('natch');

// Add event listeners to the input fields
field1.addEventListener('input', compareFields);
field2.addEventListener('input', compareFields);