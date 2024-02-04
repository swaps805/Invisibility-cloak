const btn = document.querySelector('.color_form button')

function updateAndResetForm() {
    var lowerHue = document.querySelector('.lower_hue').value;
    var lowerSaturation = document.querySelector('.lower_saturation').value;
    var lowerValue = document.querySelector('.lower_value').value;
    var upperHue = document.querySelector('.upper_hue').value;
    var upperSaturation = document.querySelector('.upper_saturation').value;
    var upperValue = document.querySelector('.upper_value').value;

    // Make an AJAX request to update_color_values route
    fetch('/update_color', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            lower_hue: lowerHue,
            lower_saturation: lowerSaturation,
            lower_value: lowerValue,
            upper_hue: upperHue,
            upper_saturation: upperSaturation,
            upper_value: upperValue,
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Update successful:', data);
    })
    .catch(error => {
        console.error('Error updating values:', error);
    });

    console.log("Updated Values:", lowerHue, lowerSaturation, lowerValue, upperHue, upperSaturation, upperValue);
    
}

btn.addEventListener('click', () => {
    console.log("clicked")
    updateAndResetForm()
});
