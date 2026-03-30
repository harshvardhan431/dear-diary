document.getElementById("state").addEventListener("change", function () {
    const stateId = this.value;
    const citySelect = document.getElementById("city");

    citySelect.innerHTML = "";
    citySelect.disabled = true;

    if (!stateId) return;

    fetch(`/cities/${stateId}`)
        .then(response => response.json())
        .then(data => {
            data.forEach(city => {
                const option = document.createElement("option");
                option.value = city.id;
                option.textContent = city.name;
                citySelect.appendChild(option);
            });
            citySelect.disabled = false;
        });
});
