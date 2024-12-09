let currentInputURL = ""; // To store the user-entered URL

document.addEventListener("DOMContentLoaded", () => {
  const calculateButton = document.getElementById("calculateButton");
  const urlInput = document.getElementById("urlInput");
  const statusDiv = document.getElementById("statusDiv");

  calculateButton.addEventListener("click", async () => {
    const input_data = urlInput.value.trim();
    if (!input_data) {
      statusDiv.textContent = "Please provide a URL or ingredients.";
      return;
    }

    currentInputURL = input_data; // Store the URL user provided

    statusDiv.textContent = "Calculating CO2 Emission (this may take a minute or two)...";

    try {
      const startResponse = await fetch(`/calculate?input_data=${encodeURIComponent(input_data)}`);
      if (startResponse.status !== 202) {
        statusDiv.textContent = "Error starting estimation.";
        return;
      }

      const startData = await startResponse.json();
      const inputHash = startData.hashed_input;
      pollForResult(inputHash);
    } catch (error) {
      statusDiv.textContent = `An error occurred: ${error.message}`;
    }
  });
});

async function pollForResult(inputHash) {
  const statusDiv = document.getElementById("statusDiv");
  try {
    const response = await fetch(`/results/${inputHash}`);
    const data = await response.json();

    if (data.status === "Processing") {
      statusDiv.textContent = "Still working on it ... please wait.";
      setTimeout(() => pollForResult(inputHash), 2000);
    } else if (data.status === "Completed") {
      const parsedData = JSON.parse(data.result);
      updateUI(parsedData);
      // Clear the status message
      statusDiv.textContent = "";
    } else {
      statusDiv.textContent = "Unexpected response status.";
    }
  } catch (error) {
    statusDiv.textContent = `An error occurred: ${error.message}`;
  }
}

function updateUI(parsedData) {
  // Use the user-provided URL for the iframe:
  const recipeFrame = document.getElementById("recipeFrame");
  recipeFrame.src = currentInputURL;

  // Update summary
  document.getElementById("totalCO2").textContent = parsedData.total_co2_kg || "N/A";
  document.getElementById("numberOfPersons").textContent = parsedData.number_of_persons || "N/A";
  document.getElementById("co2PerPerson").textContent = parsedData.co2_per_person_kg || "N/A";

  const avgRange = parsedData.avg_meal_emission_per_person_range_kg;
  if (avgRange && avgRange.length === 2) {
    document.getElementById("avgRange").textContent = `${avgRange[0]} - ${avgRange[1]}`;
  } else {
    document.getElementById("avgRange").textContent = "N/A";
  }

  // Update ingredients grid
  const cardsContainer = document.getElementById("ingredientCards");
  cardsContainer.innerHTML = "";

  parsedData.ingredients.forEach(ing => {
    const card = document.createElement("div");
    card.className = "ingredient-card";

    // Placeholder image
    const img = document.createElement("img");
    img.src = "placeholder.jpg"; // Replace with a real placeholder if desired
    img.alt = ing.name;

    const title = document.createElement("h5");
    title.textContent = ing.name;

    const weight = document.createElement("p");
    weight.textContent = `Weight: ${ing.weight_kg !== null ? ing.weight_kg + " kg" : "N/A"}`;

    const co2 = document.createElement("p");
    co2.textContent = `CO2: ${ing.co2_kg !== null ? ing.co2_kg + " kg" : "N/A"}`;


    card.appendChild(img);
    card.appendChild(title);
    card.appendChild(weight);
    card.appendChild(co2);
    cardsContainer.appendChild(card);
  });
}
