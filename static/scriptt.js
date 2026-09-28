document
    
    .addEventListener("submit", function(event) {

        event.preventDefault();

        let name = document.getElementById("name").value;

        alert(
            "Thank you " + name +
            "! Your event enquiry has been received."
        );

        document.getElementById("eventForm").reset();

    });